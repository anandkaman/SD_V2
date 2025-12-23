# backend/test_single_pdf.py

"""
Test script to process a single PDF through the complete pipeline
"""

import sys
from pathlib import Path
import logging

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent))

from app.services.pdf_processor import PDFProcessor
from app.database import get_db
from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_pdf(pdf_path: str):
    """Test processing of a single PDF"""
    pdf_file = Path(pdf_path)
    
    if not pdf_file.exists():
        logger.error(f"PDF file not found: {pdf_path}")
        return
    
    logger.info("="*60)
    logger.info(f"Testing PDF Processing: {pdf_file.name}")
    logger.info("="*60)
    
    # Initialize processor
    processor = PDFProcessor()
    
    # Process PDF
    with get_db() as db:
        result = processor.process_single_pdf(pdf_file, db)
    
    # Print results
    logger.info("\n" + "="*60)
    logger.info("PROCESSING RESULT")
    logger.info("="*60)
    logger.info(f"Document ID: {result['document_id']}")
    logger.info(f"Status: {result['status']}")
    logger.info(f"Registration Fee: {result['registration_fee']}")
    logger.info(f"LLM Extracted: {result['llm_extracted']}")
    logger.info(f"Saved to DB: {result['saved_to_db']}")
    
    if result['error']:
        logger.error(f"Error: {result['error']}")
    
    logger.info("="*60)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Usage: python test_single_pdf.py <path_to_pdf>")
        logger.info("Example: python test_single_pdf.py data/newly_uploaded/test.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    test_pdf(pdf_path)