# backend/app/workers/pipeline_batch_processor.py

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict, Callable
import logging
from threading import Lock
from queue import Queue
from app.config import settings
from app.database import get_db_context

logger = logging.getLogger(__name__)

class PipelineBatchProcessor:
    """
    Pipeline-based batch processor that splits work into stages:
    - Stage 1 (CPU-intensive): RegFee extraction + OCR
    - Stage 2 (IO-intensive): LLM + Validation + DB save

    This allows OCR workers to start new PDFs while LLM workers are processing,
    maximizing CPU utilization.
    """

    def __init__(self, max_workers: int = None):
        """
        Initialize pipeline processor

        Args:
            max_workers: Number of workers per stage (actual workers = 2 * max_workers)
        """
        self.max_workers = max_workers or settings.MAX_WORKERS
        self.is_running = False
        self.lock = Lock()

        # Queue for passing data between stages
        self.ocr_to_llm_queue = Queue()

        self.stats = {
            "total": 0,
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "stopped": 0,
            "current_file": None,
            "stage1_active": 0,  # OCR workers
            "stage2_active": 0,  # LLM workers
        }

        logger.info(f"Pipeline Batch Processor initialized with {self.max_workers} workers per stage")

    def get_stats(self) -> Dict:
        """Get current processing statistics"""
        with self.lock:
            stats = self.stats.copy()
            stats["is_running"] = self.is_running
            # Total active workers = Stage 1 + Stage 2
            stats["active_workers"] = (
                (self.max_workers if self.is_running else 0) * 2
            )
            return stats

    def update_stats(self, **kwargs):
        """Thread-safe stats update"""
        with self.lock:
            self.stats.update(kwargs)

    def process_batch(
        self,
        pdf_files: List[Path],
        stage1_func: Callable,  # OCR processing
        stage2_func: Callable,  # LLM processing
        progress_callback: Callable = None
    ) -> Dict:
        """
        Process PDFs using pipeline parallelism

        Args:
            pdf_files: List of PDF file paths
            stage1_func: Function for Stage 1 (RegFee + OCR)
            stage2_func: Function for Stage 2 (LLM + DB)
            progress_callback: Optional callback

        Returns:
            Summary of results
        """
        self.is_running = True
        total_files = len(pdf_files)

        self.update_stats(
            total=total_files,
            processed=0,
            successful=0,
            failed=0,
            stopped=0,
            current_file=None,
            stage1_active=0,
            stage2_active=0
        )

        logger.info(f"Starting pipeline processing: {total_files} files with {self.max_workers}x2 workers")

        results = []

        try:
            # Stage 1: OCR Pool (CPU-intensive)
            with ThreadPoolExecutor(max_workers=self.max_workers) as ocr_executor:
                # Stage 2: LLM Pool (IO-intensive, waiting for API)
                with ThreadPoolExecutor(max_workers=self.max_workers) as llm_executor:

                    # Submit Stage 1 tasks (OCR)
                    stage1_futures = {}
                    for pdf_path in pdf_files:
                        future = ocr_executor.submit(
                            self._stage1_ocr,
                            stage1_func,
                            pdf_path
                        )
                        stage1_futures[future] = pdf_path

                    # Submit Stage 2 tasks (LLM) as Stage 1 completes
                    stage2_futures = {}
                    completed_count = 0

                    for future in as_completed(stage1_futures):
                        if not self.is_running:
                            logger.info("Pipeline processing stopped by user")
                            ocr_executor.shutdown(wait=False)
                            llm_executor.shutdown(wait=False)
                            break

                        pdf_path = stage1_futures[future]

                        try:
                            stage1_result = future.result()

                            if stage1_result["status"] == "success":
                                # Submit to Stage 2
                                stage2_future = llm_executor.submit(
                                    self._stage2_llm,
                                    stage2_func,
                                    stage1_result
                                )
                                stage2_futures[stage2_future] = pdf_path
                            else:
                                # Stage 1 failed, record result
                                results.append(stage1_result)
                                completed_count += 1
                                self._update_progress(completed_count, total_files, stage1_result, progress_callback)

                        except Exception as e:
                            logger.error(f"Stage 1 error for {pdf_path.name}: {e}")
                            results.append({
                                "document_id": pdf_path.name,
                                "status": "failed",
                                "error": f"Stage 1 error: {str(e)}"
                            })
                            completed_count += 1

                    # Wait for Stage 2 to complete
                    for future in as_completed(stage2_futures):
                        if not self.is_running:
                            break

                        pdf_path = stage2_futures[future]

                        try:
                            stage2_result = future.result()
                            results.append(stage2_result)
                            completed_count += 1
                            self._update_progress(completed_count, total_files, stage2_result, progress_callback)

                        except Exception as e:
                            logger.error(f"Stage 2 error for {pdf_path.name}: {e}")
                            results.append({
                                "document_id": pdf_path.name,
                                "status": "failed",
                                "error": f"Stage 2 error: {str(e)}"
                            })
                            completed_count += 1

        finally:
            self.is_running = False

        # Summary
        summary = {
            "total": total_files,
            "processed": self.stats["processed"],
            "successful": self.stats["successful"],
            "failed": self.stats["failed"],
            "results": results
        }

        logger.info(f"Pipeline processing completed: {summary['successful']}/{summary['total']} successful")

        return summary

    def _stage1_ocr(self, stage1_func: Callable, pdf_path: Path) -> Dict:
        """
        Stage 1: CPU-intensive (RegFee + OCR)
        """
        with self.lock:
            self.stats["stage1_active"] += 1

        try:
            with get_db_context() as db:
                result = stage1_func(pdf_path, db)
                return result
        finally:
            with self.lock:
                self.stats["stage1_active"] -= 1

    def _stage2_llm(self, stage2_func: Callable, stage1_result: Dict) -> Dict:
        """
        Stage 2: IO-intensive (LLM + Validation + DB)
        """
        with self.lock:
            self.stats["stage2_active"] += 1

        try:
            with get_db_context() as db:
                result = stage2_func(stage1_result, db)
                return result
        finally:
            with self.lock:
                self.stats["stage2_active"] -= 1

    def _update_progress(self, completed: int, total: int, result: Dict, callback: Callable):
        """Update progress stats"""
        successful = result["status"] == "success"
        failed = result["status"] == "failed"
        stopped = result["status"] == "stopped"

        with self.lock:
            self.stats["processed"] = completed
            if successful:
                self.stats["successful"] += 1
            if failed:
                self.stats["failed"] += 1
            if stopped:
                self.stats["stopped"] += 1

        if callback:
            callback(completed, total, result)

        logger.info(f"Progress: {completed}/{total} - {result.get('document_id', 'UNKNOWN')}: {result['status']}")

    def stop(self):
        """Stop pipeline processing"""
        logger.info("Stopping pipeline processor...")
        self.is_running = False
