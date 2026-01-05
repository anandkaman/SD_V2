# backend/app/workers/pipeline_processor_v2.py

"""
Pipeline Batch Processor - Version 2

This processor implements true pipeline parallelism with separate worker pools:
- OCR Pool: CPU-intensive tasks (RegFee extraction + Tesseract OCR)
- LLM Pool: I/O-intensive tasks (LLM API calls + Validation + DB save)

Architecture:
  [PDF Files] → [OCR Pool (5 workers)] → [Queue] → [LLM Pool (5 workers)] → [Complete]

Benefits:
- Maximum CPU utilization (OCR workers always busy)
- No blocking during LLM API waits
- True parallelism: 10 PDFs processing simultaneously (5 OCR + 5 LLM)
- Automatic load balancing via queue
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict, Callable, Optional
from queue import Queue, Empty
from dataclasses import dataclass
import logging
from threading import Lock
from app.config import settings
from app.database import get_db_context

logger = logging.getLogger(__name__)


@dataclass
class Stage1Result:
    """Data structure for passing results from Stage 1 to Stage 2"""
    pdf_path: Path
    document_id: str
    registration_fee: Optional[float]  # From pdfplumber
    new_ocr_reg_fee: Optional[float]  # From OCR text
    ocr_text: str
    status: str
    error: Optional[str] = None
    pdf_images: Optional[List] = None  # PIL Images from OCR conversion (for YOLO reuse)


class PipelineBatchProcessor:
    """
    Pipeline processor with separate OCR and LLM worker pools
    """

    def __init__(self, max_ocr_workers: int = None, max_llm_workers: int = None):
        """
        Initialize pipeline processor

        Args:
            max_ocr_workers: Number of OCR workers (default from config)
            max_llm_workers: Number of LLM workers (default from config)
        """
        self.max_ocr_workers = max_ocr_workers or settings.MAX_OCR_WORKERS
        self.max_llm_workers = max_llm_workers or settings.MAX_LLM_WORKERS
        self.is_running = False
        self.lock = Lock()

        self.stats = {
            "total": 0,
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "stopped": 0,
            "ocr_active": 0,      # Currently processing in OCR stage
            "llm_active": 0,      # Currently processing in LLM stage
            "in_queue": 0,        # Waiting in queue between stages
            "current_file": None
        }

        logger.info(
            f"Pipeline Processor V2 initialized: "
            f"{self.max_ocr_workers} OCR workers + "
            f"{self.max_llm_workers} LLM workers + "
            f"Stage-2 Queue Size: {settings.STAGE2_QUEUE_SIZE}"
        )

    def get_stats(self) -> Dict:
        """Get current processing statistics"""
        with self.lock:
            stats = self.stats.copy()
            stats["is_running"] = self.is_running
            stats["active_workers"] = (
                (self.max_ocr_workers + self.max_llm_workers) if self.is_running else 0
            )
            stats["ocr_workers"] = self.max_ocr_workers if self.is_running else 0
            stats["llm_workers"] = self.max_llm_workers if self.is_running else 0
            return stats

    def update_stats(self, **kwargs):
        """Thread-safe stats update"""
        with self.lock:
            self.stats.update(kwargs)

    def process_batch(
        self,
        pdf_files: List[Path],
        stage1_processor,  # PDFProcessor instance for stage 1
        stage2_processor,  # PDFProcessor instance for stage 2
        progress_callback: Callable = None
    ) -> Dict:
        """
        Process PDFs using pipeline parallelism with bounded queue backpressure

        Args:
            pdf_files: List of PDF file paths
            stage1_processor: Processor for Stage 1 (OCR)
            stage2_processor: Processor for Stage 2 (LLM)
            progress_callback: Optional callback for progress updates

        Returns:
            Summary of batch processing results
        """
        self.is_running = True
        total_files = len(pdf_files)

        self.update_stats(
            total=total_files,
            processed=0,
            successful=0,
            failed=0,
            stopped=0,
            ocr_active=0,
            llm_active=0,
            in_queue=0,
            current_file=None
        )

        logger.info(
            f"Starting pipeline processing: {total_files} files "
            f"({self.max_ocr_workers} OCR + {self.max_llm_workers} LLM workers), "
            f"Stage-2 Queue Size: {settings.STAGE2_QUEUE_SIZE}"
        )

        results = []
        # Bounded queue to prevent memory overflow if LLM stage is slower than OCR
        # Stage 1 will BLOCK when queue is full, providing backpressure
        stage2_queue = Queue(maxsize=settings.STAGE2_QUEUE_SIZE)

        try:
            # Create both worker pools
            with ThreadPoolExecutor(max_workers=self.max_ocr_workers) as ocr_executor, \
                 ThreadPoolExecutor(max_workers=self.max_llm_workers) as llm_executor:

                # Submit all PDFs to Stage 1 (OCR)
                stage1_futures = {}
                for pdf_path in pdf_files:
                    future = ocr_executor.submit(
                        self._stage1_ocr_with_queue,
                        stage1_processor,
                        pdf_path,
                        stage2_queue
                    )
                    stage1_futures[future] = pdf_path

                # Submit LLM workers to process from queue
                stage2_futures = {}
                for _ in range(self.max_llm_workers):
                    future = llm_executor.submit(
                        self._stage2_llm_consumer,
                        stage2_processor,
                        stage2_queue,
                        results,
                        progress_callback
                    )
                    stage2_futures[future] = None

                # Monitor Stage 1 completion
                stage1_completed = 0
                for future in as_completed(stage1_futures):
                    if not self.is_running:
                        logger.info("Pipeline processing stopped by user")
                        # Signal all LLM workers to stop
                        for _ in range(self.max_llm_workers):
                            stage2_queue.put(None)
                        ocr_executor.shutdown(wait=False)
                        break

                    pdf_path = stage1_futures[future]

                    try:
                        stage1_result = future.result()
                        stage1_completed += 1

                        logger.info(
                            f"Stage 1 complete ({stage1_completed}/{total_files}): "
                            f"{stage1_result.document_id if stage1_result else pdf_path.stem} - "
                            f"{stage1_result.status if stage1_result else 'unknown'}"
                        )

                        # Handle Stage 1 failures - add to results and update stats
                        if stage1_result and stage1_result.status != "success":
                            failure_result = {
                                "document_id": stage1_result.document_id,
                                "status": stage1_result.status,
                                "error": stage1_result.error,
                                "registration_fee": stage1_result.registration_fee,
                                "llm_extracted": False,
                                "saved_to_db": False
                            }
                            results.append(failure_result)
                            self._update_completion_stats(failure_result, progress_callback)

                    except Exception as e:
                        logger.error(f"Stage 1 exception for {pdf_path.name}: {e}")
                        error_result = {
                            "document_id": pdf_path.stem,
                            "status": "failed",
                            "error": f"Stage 1 exception: {str(e)}",
                            "llm_extracted": False,
                            "saved_to_db": False
                        }
                        results.append(error_result)
                        self._update_completion_stats(error_result, progress_callback)

                # Signal LLM workers that Stage 1 is complete (send None sentinel)
                logger.info("Stage 1 complete, signaling Stage 2 workers to finish")
                for _ in range(self.max_llm_workers):
                    stage2_queue.put(None)

                # Wait for all Stage 2 workers to complete
                for future in as_completed(stage2_futures):
                    try:
                        future.result()  # Just wait for completion
                    except Exception as e:
                        logger.error(f"Stage 2 worker exception: {e}")

        finally:
            self.is_running = False

        # Summary
        summary = {
            "total": total_files,
            "processed": self.stats["processed"],
            "successful": self.stats["successful"],
            "failed": self.stats["failed"],
            "stopped": self.stats["stopped"],
            "results": results
        }

        logger.info(
            f"Pipeline processing completed: {summary['successful']}/{summary['total']} successful"
        )

        # ✅ UPDATE BATCH STATUS TO COMPLETED
        try:
            from app.database import get_db_context
            from app.models import BatchSession
            
            with get_db_context() as db:
                # Get the most recent processing batch
                batch_session = db.query(BatchSession).filter(
                    BatchSession.status == 'processing'
                ).order_by(BatchSession.processing_started_at.desc()).first()
                
                if batch_session:
                    batch_session.status = 'completed'
                    batch_session.processed_count = summary['successful']
                    batch_session.failed_count = summary['failed']
                    db.commit()
                    logger.info(f"Updated batch {batch_session.batch_id} status to completed")
                    
                    # ✅ CREATE BATCH COMPLETION NOTIFICATION
                    try:
                        from app.services.notification_service import notification_service
                        
                        notification_service.create_batch_completion_notification(
                            db=db,
                            batch_id=batch_session.batch_id,
                            batch_name=batch_session.batch_name or batch_session.batch_id,
                            total_files=summary['total'],
                            successful=summary['successful'],
                            failed=summary['failed']
                        )
                        logger.info(f"Batch completion notification created for {batch_session.batch_id}")
                    except Exception as notif_error:
                        logger.warning(f"Could not create batch completion notification: {notif_error}")
                        
        except Exception as e:
            logger.warning(f"Could not update batch session status: {e}")

        return summary

    def _stage1_ocr_with_queue(self, processor, pdf_path: Path, queue: Queue) -> Stage1Result:
        """
        Stage 1: CPU-intensive processing (RegFee + OCR)
        Puts successful results into queue for Stage 2
        Stage 1 will BLOCK if queue is full (backpressure)
        """
        self.update_stats(
            ocr_active=self.stats["ocr_active"] + 1,
            current_file=pdf_path.name
        )

        try:
            with get_db_context() as db:
                result = processor.process_stage1_ocr(pdf_path, db)

                if result.status == "success":
                    # Put result in queue - THIS BLOCKS if queue is full
                    logger.info(f"[{result.document_id}] Waiting to add to Stage 2 queue (size={queue.qsize()}/{queue.maxsize})")
                    queue.put(result)  # BLOCKS when queue is full!
                    self.update_stats(in_queue=self.stats["in_queue"] + 1)
                    logger.info(f"[{result.document_id}] Added to Stage 2 queue")

                return result

        finally:
            self.update_stats(ocr_active=self.stats["ocr_active"] - 1)

    def _stage2_llm_consumer(self, processor, queue: Queue, results: list, progress_callback: Callable):
        """
        Stage 2: Consumer worker that processes items from queue
        Multiple workers run this function concurrently
        """
        while self.is_running:
            try:
                # Get Stage 1 result from queue (blocks until available)
                stage1_result = queue.get(timeout=1.0)

                # None is sentinel value to signal worker shutdown
                if stage1_result is None:
                    logger.info("Stage 2 worker received shutdown signal")
                    break

                # Update stats
                self.update_stats(
                    llm_active=self.stats["llm_active"] + 1,
                    in_queue=self.stats["in_queue"] - 1,
                    current_file=stage1_result.document_id
                )

                try:
                    # Process with LLM
                    with get_db_context() as db:
                        result = processor.process_stage2_llm(stage1_result, db)
                        results.append(result)

                        logger.info(
                            f"Stage 2 complete: {result['document_id']} - "
                            f"{result['status']}"
                        )

                        self._update_completion_stats(result, progress_callback)

                finally:
                    self.update_stats(llm_active=self.stats["llm_active"] - 1)
                    queue.task_done()

            except Empty:
                # Queue timeout - this is normal, just continue waiting
                continue
            except Exception as e:
                logger.error(f"Stage 2 consumer error: {e}", exc_info=True)

        logger.info("Stage 2 worker exiting")

    def _update_completion_stats(self, result: Dict, callback: Callable):
        """Update completion statistics"""
        processed = self.stats["processed"] + 1
        successful = self.stats["successful"] + (1 if result["status"] == "success" else 0)
        failed = self.stats["failed"] + (1 if result["status"] == "failed" else 0)
        stopped = self.stats["stopped"] + (1 if result["status"] == "stopped" else 0)

        self.update_stats(
            processed=processed,
            successful=successful,
            failed=failed,
            stopped=stopped
        )

        if callback:
            callback(processed, self.stats["total"], result)

    def stop(self):
        """Stop pipeline processing"""
        logger.info("Stopping pipeline processor...")
        self.is_running = False
