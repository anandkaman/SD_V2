# backend/app/workers/vision_batch_processor.py

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict
import logging
import os
import shutil
from threading import Lock
from sqlalchemy.orm import Session

from app.config import settings
from app.services.vision_service_factory import get_vision_service
from app.services.validation_service import ValidationService
from app.database import get_db_context
from app.models import PropertyDetail

logger = logging.getLogger(__name__)

class VisionBatchProcessor:
    def __init__(self, max_workers: int = 1):
        """Initialize vision batch processor (max_workers=1 for sequential processing)"""
        self.max_workers = max_workers
        self.vision_service = get_vision_service()
        self.is_running = False
        self.lock = Lock()
        self.stats = {
            "total": 0,
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "stopped": 0
        }

        logger.info(f"Vision Batch Processor initialized with {self.max_workers} workers")
    
    def get_stats(self) -> Dict:
        """Get current processing statistics"""
        with self.lock:
            stats = self.stats.copy()
            stats["is_running"] = self.is_running
            stats["active_workers"] = self.max_workers if self.is_running else 0
            return stats
    
    def update_stats(self, **kwargs):
        """Thread-safe stats update"""
        with self.lock:
            self.stats.update(kwargs)
    
    def process_batch(self, image_files: List[Path] = None) -> Dict:
        """
        Process cropped table images with vision model
        
        Args:
            image_files: List of image paths (if None, scans left_over_reg_fee folder)
            
        Returns:
            Processing summary
        """
        if image_files is None:
            image_files = list(settings.LEFT_OVER_REG_FEE_DIR.glob("*.png"))
            image_files.extend(settings.LEFT_OVER_REG_FEE_DIR.glob("*.jpg"))
        
        self.is_running = True
        total_files = len(image_files)
        
        self.update_stats(
            total=total_files,
            processed=0,
            successful=0,
            failed=0,
            stopped=0
        )
        
        logger.info(f"Starting vision batch processing: {total_files} images")
        
        results = []
        
        try:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_image = {}
                for image_path in image_files:
                    future = executor.submit(self._process_single_image, image_path)
                    future_to_image[future] = image_path
                
                for future in as_completed(future_to_image):
                    if not self.is_running:
                        logger.info("Vision batch processing stopped")
                        executor.shutdown(wait=False)
                        break
                    
                    image_path = future_to_image[future]
                    
                    try:
                        result = future.result()
                        results.append(result)

                        processed = self.stats["processed"] + 1
                        successful = self.stats["successful"] + (1 if result["success"] else 0)
                        # Don't count stopped as failed
                        failed = self.stats["failed"] + (1 if not result["success"] and not result.get("stopped", False) else 0)
                        stopped = self.stats["stopped"] + (1 if result.get("stopped", False) else 0)

                        self.update_stats(
                            processed=processed,
                            successful=successful,
                            failed=failed,
                            stopped=stopped
                        )
                        
                        logger.info(f"Vision progress: {processed}/{total_files} - {image_path.name}")
                        
                    except Exception as e:
                        logger.error(f"Error processing {image_path.name}: {e}")
        
        finally:
            self.is_running = False
        
        summary = {
            "total": total_files,
            "processed": self.stats["processed"],
            "successful": self.stats["successful"],
            "failed": self.stats["failed"],
            "stopped": self.stats["stopped"],
            "results": results
        }
        
        logger.info(f"Vision batch completed: {summary['successful']}/{summary['total']} successful")
        
        return summary
    
    def _process_single_image(self, image_path: Path) -> Dict:
        """Process single image and update database"""
        from app.exceptions import ProcessingStoppedException

        result = {
            "image": image_path.name,
            "document_id": None,
            "registration_fee": None,
            "success": False,
            "stopped": False,
            "error": None
        }

        try:
            # Check if stopped before processing
            if not self.is_running:
                raise ProcessingStoppedException("Vision processing stopped by user")

            # Extract document ID from filename (format: documentid_page_X.png)
            filename_parts = image_path.stem.split("_page_")
            if len(filename_parts) != 2:
                # Try alternative: documentid_table.png
                document_id = image_path.stem.replace("_table", "")
            else:
                document_id = filename_parts[0]

            result["document_id"] = document_id

            # Extract registration fee using vision model
            reg_fee = self.vision_service.extract_registration_fee(str(image_path))

            # Vision model exception: Accept any positive value (no MIN_REGISTRATION_FEE check)
            # Vision can extract values from bad prints that would otherwise be rejected
            if reg_fee and reg_fee > 0:
                result["registration_fee"] = reg_fee
                if reg_fee < settings.MIN_REGISTRATION_FEE:
                    logger.info(f"Vision extracted fee {reg_fee} is below MIN threshold ({settings.MIN_REGISTRATION_FEE}), but accepting anyway (vision exception)")

                # Check again before database update
                if not self.is_running:
                    raise ProcessingStoppedException("Vision processing stopped before DB update")

                # Update database
                with get_db_context() as db:
                    prop = db.query(PropertyDetail).filter(
                        PropertyDetail.document_id == document_id
                    ).first()

                    if prop:
                        # Format registration fee as string (consistent with pdfplumber extraction)
                        # Remove trailing .0 if it's a whole number, otherwise keep 2 decimals
                        if isinstance(reg_fee, float):
                            if reg_fee == int(reg_fee):
                                prop.registration_fee = str(int(reg_fee))
                            else:
                                prop.registration_fee = f"{reg_fee:.2f}"
                        else:
                            prop.registration_fee = str(reg_fee)

                        # Calculate and format guidance value
                        guidance_val = ValidationService.calculate_guidance_value(reg_fee)
                        if isinstance(guidance_val, float):
                            if guidance_val == int(guidance_val):
                                prop.guidance_value = str(int(guidance_val))
                            else:
                                prop.guidance_value = f"{guidance_val:.2f}"
                        else:
                            prop.guidance_value = str(guidance_val)

                        result["success"] = True
                        logger.info(f"Updated {document_id} with registration fee: {reg_fee}")

                        # Delete the image file after successful processing
                        try:
                            os.remove(image_path)
                            logger.info(f"Deleted processed image: {image_path.name}")
                        except Exception as e:
                            logger.warning(f"Failed to delete image {image_path.name}: {e}")
                    else:
                        result["error"] = f"Document {document_id} not found in database"
                        # Move to vision_failed folder
                        self._move_to_failed(image_path, result["error"])
            else:
                result["error"] = "Invalid or no registration fee extracted"
                # Move to vision_failed folder
                self._move_to_failed(image_path, result["error"])

        # Handle stopped processing separately
        except ProcessingStoppedException as stopped_ex:
            logger.info(f"Vision processing stopped: {image_path.name}")
            result["stopped"] = True
            result["error"] = stopped_ex.message
            # DO NOT move to vision_failed - keep in left_over_reg_fee

        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Error processing {image_path.name}: {e}")
            # Move to vision_failed folder on actual exception
            self._move_to_failed(image_path, str(e))

        return result

    def _move_to_failed(self, image_path: Path, reason: str):
        """Move failed image to vision_failed folder"""
        try:
            failed_path = settings.VISION_FAILED_DIR / image_path.name
            shutil.move(str(image_path), str(failed_path))
            logger.info(f"Moved failed image to vision_failed: {image_path.name} - Reason: {reason}")
        except Exception as e:
            logger.error(f"Failed to move {image_path.name} to vision_failed folder: {e}")
    
    def stop(self):
        """Stop vision batch processing"""
        logger.info("Stopping vision batch processor...")
        self.is_running = False