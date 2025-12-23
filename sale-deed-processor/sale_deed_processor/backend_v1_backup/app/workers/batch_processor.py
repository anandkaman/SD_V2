# backend/app/workers/batch_processor.py

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict, Callable
import logging
from threading import Lock
from app.config import settings
from app.database import get_db_context

logger = logging.getLogger(__name__)

class BatchProcessor:
    def __init__(self, max_workers: int = None):
        """
        Initialize batch processor with worker pool
        
        Args:
            max_workers: Maximum number of worker threads
        """
        self.max_workers = max_workers or settings.MAX_WORKERS
        self.is_running = False
        self.lock = Lock()
        self.stats = {
            "total": 0,
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "stopped": 0,
            "current_file": None
        }
        
        logger.info(f"Batch Processor initialized with {self.max_workers} workers")
    
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
    
    def process_batch(
        self,
        pdf_files: List[Path],
        process_func: Callable,
        progress_callback: Callable = None
    ) -> Dict:
        """
        Process multiple PDFs in parallel using thread pool
        
        Args:
            pdf_files: List of PDF file paths
            process_func: Function to process each PDF (should accept pdf_path and db session)
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
            current_file=None
        )
        
        logger.info(f"Starting batch processing: {total_files} files with {self.max_workers} workers")
        
        results = []
        
        try:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all tasks
                future_to_pdf = {}
                for pdf_path in pdf_files:
                    future = executor.submit(self._process_with_db, process_func, pdf_path)
                    future_to_pdf[future] = pdf_path
                
                # Process completed tasks
                for future in as_completed(future_to_pdf):
                    if not self.is_running:
                        logger.info("Batch processing stopped by user")
                        executor.shutdown(wait=False)
                        break
                    
                    pdf_path = future_to_pdf[future]
                    
                    try:
                        result = future.result()
                        results.append(result)

                        # Update stats
                        processed = self.stats["processed"] + 1
                        successful = self.stats["successful"] + (1 if result["status"] == "success" else 0)
                        failed = self.stats["failed"] + (1 if result["status"] == "failed" else 0)
                        stopped = self.stats["stopped"] + (1 if result["status"] == "stopped" else 0)

                        self.update_stats(
                            processed=processed,
                            successful=successful,
                            failed=failed,
                            stopped=stopped,
                            current_file=None
                        )
                        
                        # Progress callback
                        if progress_callback:
                            progress_callback(processed, total_files, result)
                        
                        logger.info(f"Progress: {processed}/{total_files} - {pdf_path.name}: {result['status']}")
                        
                    except Exception as e:
                        logger.error(f"Error processing {pdf_path.name}: {e}")
                        results.append({
                            "document_id": pdf_path.name,
                            "status": "failed",
                            "error": str(e)
                        })
        
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
        
        logger.info(f"Batch processing completed: {summary['successful']}/{summary['total']} successful")
        
        return summary
    
    def _process_with_db(self, process_func: Callable, pdf_path: Path) -> Dict:
        """
        Wrapper to provide database session to processing function

        Args:
            process_func: Processing function
            pdf_path: Path to PDF file

        Returns:
            Processing result
        """
        with get_db_context() as db:
            self.update_stats(current_file=pdf_path.name)
            return process_func(pdf_path, db)
    
    def stop(self):
        """Stop batch processing (will complete current tasks)"""
        logger.info("Stopping batch processor...")
        self.is_running = False