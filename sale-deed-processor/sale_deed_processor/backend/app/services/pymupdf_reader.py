# backend/app/services/pymupdf_reader.py

"""
PyMuPDF (fitz) Reader - Extracts embedded OCR text from PDFs
For PDFs with high-quality embedded text/OCR
"""

import fitz  # PyMuPDF
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class PyMuPDFReader:
    """
    Reader to extract embedded OCR text from PDFs using PyMuPDF (fitz).
    Useful for PDFs with high-quality embedded text/OCR.
    """

    def __init__(self, max_pages: int = 25):
        """
        Initialize PyMuPDF reader

        Args:
            max_pages: Maximum number of pages to extract (default 25)
        """
        self.max_pages = max_pages
        logger.info(f"PyMuPDF Reader initialized (max {max_pages} pages)")

    def extract_text(self, pdf_path: str) -> Optional[str]:
        """
        Extract embedded text from PDF using PyMuPDF

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text or None if failed
        """
        try:
            pdf_path_obj = Path(pdf_path)
            if not pdf_path_obj.exists():
                logger.error(f"PDF file not found: {pdf_path}")
                return None

            logger.info(f"Extracting embedded OCR text from {pdf_path_obj.name} using PyMuPDF")

            full_text = []

            # Open PDF with PyMuPDF
            with fitz.open(pdf_path) as pdf_document:
                total_pages = len(pdf_document)
                pages_to_process = min(total_pages, self.max_pages)

                logger.info(f"Processing {pages_to_process} pages (of {total_pages} total)")

                for page_num in range(pages_to_process):
                    try:
                        page = pdf_document[page_num]

                        # Try multiple extraction methods
                        # Method 1: Default text extraction
                        text = page.get_text("text")

                        # If no text found, try extracting with layout preservation
                        if not text or len(text.strip()) < 10:
                            text = page.get_text("blocks")
                            if text:
                                # Extract text from blocks
                                text = " ".join([block[4] for block in text if len(block) > 4 and isinstance(block[4], str)])

                        if text and text.strip():
                            full_text.append(text)
                            logger.debug(f"Page {page_num + 1}: Extracted {len(text)} characters")
                        else:
                            logger.warning(f"Page {page_num + 1}: No text extracted")

                    except Exception as page_error:
                        logger.error(f"Error extracting page {page_num + 1}: {page_error}")
                        continue

            result_text = "\n\n".join(full_text)
            logger.info(f"PyMuPDF extraction complete: {len(result_text)} total characters from {len(full_text)} pages")

            if len(result_text) < 500:
                logger.warning(
                    f"Extracted text is too short ({len(result_text)} chars). "
                    f"This PDF likely does not have embedded OCR text. "
                    f"Disable 'Use Embedded OCR' toggle and use Poppler+Tesseract instead for image-based PDFs."
                )

            return result_text if result_text.strip() else None

        except Exception as e:
            logger.error(f"PyMuPDF extraction failed for {pdf_path}: {e}")
            return None

    def get_full_text(self, pdf_path: str, max_pages: Optional[int] = None) -> Optional[str]:
        """
        Get full text from PDF (convenience method matching OCRService interface)

        Args:
            pdf_path: Path to PDF file
            max_pages: Override max_pages for this extraction

        Returns:
            Extracted text or None if failed
        """
        if max_pages:
            original_max = self.max_pages
            self.max_pages = max_pages
            result = self.extract_text(pdf_path)
            self.max_pages = original_max
            return result

        return self.extract_text(pdf_path)
