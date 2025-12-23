# backend/app/services/pdf_processor.py

from pathlib import Path
from typing import Optional, Dict
import logging
from datetime import datetime
from sqlalchemy.orm import Session

from app.config import settings
from app.services.registration_fee_extractor import RegistrationFeeExtractor
from app.services.ocr_service import OCRService
from app.services.yolo_detector import YOLOTableDetector
#from app.services.llm_service import LLMService
from app.services.llm_service import get_llm_service

from app.services.validation_service import ValidationService
from app.utils.file_handler import FileHandler
from app.models import DocumentDetail, PropertyDetail, BuyerDetail, SellerDetail

logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self, batch_processor=None):
        """Initialize PDF processor with all required services

        Args:
            batch_processor: Reference to batch processor to check is_running flag
        """
        self.batch_processor = batch_processor
        self.reg_fee_extractor = RegistrationFeeExtractor(
            threshold_pct=0.7,
            max_misc_fee=settings.MAX_MISC_FEE,
            min_fee=settings.MIN_REGISTRATION_FEE
        )
        self.ocr_service = OCRService()
        self.yolo_detector = YOLOTableDetector(
            model_path=str(settings.YOLO_MODEL_PATH),
            conf_threshold=settings.YOLO_CONF_THRESHOLD
        )
        self.llm_service = get_llm_service()
        #self.llm_service = LLMService()

        logger.info("PDF Processor initialized")
    
    def process_single_pdf(self, pdf_path: Path, db: Session) -> Dict:
        """
        Process a single PDF through the complete pipeline

        Args:
            pdf_path: Path to PDF file
            db: Database session

        Returns:
            Processing result dictionary
        """
        from app.exceptions import ProcessingStoppedException

        result = {
            "document_id": None,
            "status": "failed",
            "registration_fee": None,
            "llm_extracted": False,
            "saved_to_db": False,
            "table_detected": False,
            "error": None
        }

        try:
            # Extract document ID
            document_id = FileHandler.extract_document_id(pdf_path.name)
            result["document_id"] = document_id

            logger.info(f"Processing PDF: {pdf_path.name} (Document ID: {document_id})")

            # Step 1: Try to extract registration fee using pdfplumber
            logger.info(f"[{document_id}] Step 1: Extracting registration fee with pdfplumber")
            registration_fee = self.reg_fee_extractor.extract(str(pdf_path))

            if registration_fee:
                logger.info(f"[{document_id}] Registration fee extracted: {registration_fee}")
                result["registration_fee"] = registration_fee
            else:
                logger.warning(f"[{document_id}] pdfplumber failed, will use YOLO + Vision")

            # STOP CHECK 1: After registration fee extraction, before OCR
            if self.batch_processor and not self.batch_processor.is_running:
                raise ProcessingStoppedException(f"Stopped before OCR step")

            # Step 2: Perform OCR with Tesseract (HARD LIMIT: 25 pages)
            logger.info(f"[{document_id}] Step 2: Performing OCR with Tesseract (max 25 pages)")
            full_ocr_text = self.ocr_service.get_full_text(str(pdf_path), max_pages=25)

            if not full_ocr_text or len(full_ocr_text) < 100:
                raise Exception("OCR returned insufficient text")

            logger.info(f"[{document_id}] OCR completed: {len(full_ocr_text)} characters")

            # STOP CHECK 2: After OCR, before LLM
            if self.batch_processor and not self.batch_processor.is_running:
                raise ProcessingStoppedException(f"Stopped before LLM extraction step")

            # Step 3: Extract structured data with LLM
            logger.info(f"[{document_id}] Step 3: Extracting structured data with LLM")
            extracted_data = self.llm_service.extract_structured_data(full_ocr_text)

            if not extracted_data:
                raise Exception("LLM failed to extract structured data")

            result["llm_extracted"] = True
            logger.info(f"[{document_id}] LLM extraction successful")

            # STOP CHECK 3: After LLM, before validation
            if self.batch_processor and not self.batch_processor.is_running:
                raise ProcessingStoppedException(f"Stopped before validation step")

            # Step 4: Validate and clean data
            logger.info(f"[{document_id}] Step 4: Validating and cleaning data")
            cleaned_data = ValidationService.validate_and_clean_data(extracted_data)

            # Update registration fee in property details if extracted via pdfplumber
            if registration_fee:
                cleaned_data["property_details"]["registration_fee"] = registration_fee
                cleaned_data["property_details"]["guidance_value"] = ValidationService.calculate_guidance_value(registration_fee)

            # STOP CHECK 4: Before database save
            if self.batch_processor and not self.batch_processor.is_running:
                raise ProcessingStoppedException(f"Stopped before database save step")

            # Step 5: Save to database
            logger.info(f"[{document_id}] Step 5: Saving to database")
            try:
                self._save_to_database(document_id, cleaned_data, db)
                result["saved_to_db"] = True
                logger.info(f"[{document_id}] Successfully saved to database")
            except Exception as db_error:
                logger.error(f"[{document_id}] Database save failed: {db_error}")
                raise Exception(f"Database save failed: {db_error}")

            # STOP CHECK 5: Before YOLO detection
            if self.batch_processor and not self.batch_processor.is_running:
                raise ProcessingStoppedException(f"Stopped before YOLO detection step")

            # Step 6: If registration fee not found, run YOLO detection and save cropped table
            if not registration_fee:
                logger.info(f"[{document_id}] Step 6: Running YOLO to detect and crop registration fee table")
                table_detected = self._detect_and_save_table(pdf_path, document_id)
                result["table_detected"] = table_detected

                if table_detected:
                    logger.info(f"[{document_id}] Table detected and saved for vision processing")
                else:
                    logger.warning(f"[{document_id}] No table detected by YOLO")

            # Step 7: Move to processed folder (only after successful DB save)
            result["status"] = "success"
            FileHandler.move_file(pdf_path, settings.PROCESSED_DIR)
            logger.info(f"[{document_id}] Processing completed successfully")

        # Handle stopped processing separately
        except ProcessingStoppedException as stopped_ex:
            logger.info(f"[{result.get('document_id', 'UNKNOWN')}] {stopped_ex.message}")
            result["status"] = "stopped"
            result["error"] = stopped_ex.message
            # DO NOT move file - keep in newly_uploaded for re-processing

        except Exception as e:
            logger.error(f"[{result.get('document_id', 'UNKNOWN')}] Processing failed: {e}")
            result["error"] = str(e)
            result["status"] = "failed"

            # Move to failed folder (actual failures only)
            if pdf_path.exists():
                FileHandler.move_file(pdf_path, settings.FAILED_DIR)

        return result
    
    def _detect_and_save_table(self, pdf_path: Path, document_id: str) -> bool:
        """
        Convert PDF to images, detect table with YOLO, and save ONLY cropped table
        
        Args:
            pdf_path: Path to PDF file
            document_id: Document identifier
            
        Returns:
            True if table detected and saved, False otherwise
        """
        try:
            # Convert PDF to images
            images = self.ocr_service.pdf_to_images(str(pdf_path))
            logger.info(f"[{document_id}] Converted PDF to {len(images)} images for YOLO detection")
            
            # Try to detect table in each page
            for page_num, image in enumerate(images, start=1):
                # Save temporary image for YOLO
                temp_image_path = settings.LEFT_OVER_REG_FEE_DIR / f"temp_{document_id}_page_{page_num}.png"
                image.save(temp_image_path)
                
                # Output path for cropped table
                output_image_path = settings.LEFT_OVER_REG_FEE_DIR / f"{document_id}_table.png"
                
                # Run YOLO detection and crop
                cropped_table = self.yolo_detector.detect_and_crop(
                    str(temp_image_path),
                    str(output_image_path)
                )
                
                # Delete temporary image
                if temp_image_path.exists():
                    temp_image_path.unlink()
                
                # If table detected, stop (we only need one table)
                if cropped_table is not None:
                    logger.info(f"[{document_id}] Table detected on page {page_num}, cropped image saved")
                    return True
            
            # No table found in any page
            logger.warning(f"[{document_id}] No table detected in any page")
            return False
            
        except Exception as e:
            logger.error(f"[{document_id}] Error in YOLO detection: {e}")
            return False
    
    def _save_to_database(self, document_id: str, data: Dict, db: Session):
        """
        Save extracted data to database with multiple buyers/sellers
        
        Args:
            document_id: Document identifier
            data: Cleaned and validated data
            db: Database session
        """
        try:
            # Create or update document details
            doc_data = data.get("document_details", {})
            
            doc = db.query(DocumentDetail).filter(DocumentDetail.document_id == document_id).first()
            if not doc:
                doc = DocumentDetail(
                    document_id=document_id,
                    transaction_date=doc_data.get("transaction_date"),
                    registration_office=doc_data.get("registration_office")
                )
                db.add(doc)
            else:
                doc.transaction_date = doc_data.get("transaction_date")
                doc.registration_office = doc_data.get("registration_office")
                doc.updated_at = datetime.utcnow()
            
            db.flush()
            
            # Create or update property details
            prop_data = data.get("property_details", {})
            
            prop = db.query(PropertyDetail).filter(PropertyDetail.document_id == document_id).first()
            if not prop:
                prop = PropertyDetail(document_id=document_id)
                db.add(prop)
            
            prop.schedule_b_area = prop_data.get("schedule_b_area")
            prop.schedule_c_property_name = prop_data.get("schedule_c_property_name")
            prop.schedule_c_property_address = prop_data.get("schedule_c_property_address")
            prop.schedule_c_property_area = prop_data.get("schedule_c_property_area")
            prop.paid_in_cash_mode = prop_data.get("paid_in_cash_mode")
            prop.pincode = prop_data.get("pincode")
            prop.state = prop_data.get("state")
            prop.sale_consideration = prop_data.get("sale_consideration")
            prop.stamp_duty_fee = prop_data.get("stamp_duty_fee")

            # Format registration_fee as string (remove trailing .0 if present)
            reg_fee_value = prop_data.get("registration_fee")
            if reg_fee_value is not None:
                if isinstance(reg_fee_value, float):
                    # Format as string: if it's a whole number, remove .0, otherwise keep 2 decimals
                    if reg_fee_value == int(reg_fee_value):
                        prop.registration_fee = str(int(reg_fee_value))
                    else:
                        prop.registration_fee = f"{reg_fee_value:.2f}"
                else:
                    prop.registration_fee = str(reg_fee_value)
            else:
                prop.registration_fee = None

            # Format guidance_value as string (remove trailing .0 if present)
            guidance_value = prop_data.get("guidance_value")
            if guidance_value is not None:
                if isinstance(guidance_value, float):
                    # Format as string: if it's a whole number, remove .0, otherwise keep 2 decimals
                    if guidance_value == int(guidance_value):
                        prop.guidance_value = str(int(guidance_value))
                    else:
                        prop.guidance_value = f"{guidance_value:.2f}"
                else:
                    prop.guidance_value = str(guidance_value)
            else:
                prop.guidance_value = None
            
            db.flush()
            
            # Delete existing buyers and sellers for this document (to avoid duplicates on re-processing)
            db.query(BuyerDetail).filter(BuyerDetail.document_id == document_id).delete()
            db.query(SellerDetail).filter(SellerDetail.document_id == document_id).delete()
            
            # Insert all buyers (MULTIPLE ROWS with same document_id)
            buyers = data.get("buyer_details", [])
            for buyer_data in buyers:
                buyer = BuyerDetail(
                    document_id=document_id,
                    name=buyer_data.get("name"),
                    gender=buyer_data.get("gender"),
                    aadhaar_number=buyer_data.get("aadhaar_number"),
                    pan_card_number=buyer_data.get("pan_card_number"),
                    address=buyer_data.get("address"),
                    pincode=buyer_data.get("pincode"),
                    state=buyer_data.get("state"),
                    phone_number=buyer_data.get("phone_number"),
                    secondary_phone_number=buyer_data.get("secondary_phone_number"),
                    email=buyer_data.get("email")
                )
                db.add(buyer)
            
            # Insert all sellers (MULTIPLE ROWS with same document_id)
            sellers = data.get("seller_details", [])
            for seller_data in sellers:
                seller = SellerDetail(
                    document_id=document_id,
                    name=seller_data.get("name"),
                    gender=seller_data.get("gender"),
                    aadhaar_number=seller_data.get("aadhaar_number"),
                    pan_card_number=seller_data.get("pan_card_number"),
                    address=seller_data.get("address"),
                    pincode=seller_data.get("pincode"),
                    state=seller_data.get("state"),
                    phone_number=seller_data.get("phone_number"),
                    secondary_phone_number=seller_data.get("secondary_phone_number"),
                    email=seller_data.get("email"),
                    property_share=seller_data.get("property_share")
                )
                db.add(seller)
            
            db.commit()
            logger.info(f"[{document_id}] Saved to database: {len(buyers)} buyers, {len(sellers)} sellers")
            
        except Exception as e:
            db.rollback()
            logger.error(f"[{document_id}] Database save error: {e}")
            raise