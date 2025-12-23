# backend/app/services/ocr_service.py

import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from typing import List, Dict, Optional
import logging
from multiprocessing import Pool
from functools import partial
from app.config import settings
import tempfile
import os

logger = logging.getLogger(__name__)

class OCRService:
    def __init__(
        self,
        lang: str = None,
        oem: int = None,
        psm: int = None,
        poppler_path: str = None,
        dpi: int = None
    ):
        """
        Initialize OCR service
        
        Args:
            lang: Tesseract language (default from config)
            oem: OCR Engine Mode (default from config)
            psm: Page Segmentation Mode (default from config)
            poppler_path: Path to Poppler binaries (default from config)
            dpi: DPI for PDF conversion (default from config)
        """
        self.lang = lang or settings.TESSERACT_LANG
        self.oem = oem or settings.TESSERACT_OEM
        self.psm = psm or settings.TESSERACT_PSM
        self.poppler_path = poppler_path or settings.POPPLER_PATH
        self.dpi = dpi or settings.POPPLER_DPI
        
        self.tesseract_config = f'--oem {self.oem} --psm {self.psm}'
        logger.info(
            f"OCR Service initialized: lang={self.lang}, oem={self.oem}, psm={self.psm}, dpi={self.dpi}, "
            f"multiprocessing={'enabled' if settings.ENABLE_OCR_MULTIPROCESSING else 'disabled'}"
        )
    
    def pdf_to_images(self, pdf_path: str, max_pages: Optional[int] = None) -> List[Image.Image]:
        """
        Convert PDF to list of images using Poppler and standardize resolution

        Args:
            pdf_path: Path to PDF file
            max_pages: Maximum number of pages to convert (default: None = all pages)

        Returns:
            List of PIL Image objects (standardized to ~1500px width for optimal OCR)
        """
        try:
            images = convert_from_path(
                pdf_path,
                dpi=self.dpi,
                poppler_path=self.poppler_path if self.poppler_path else None,
                last_page=max_pages  # Poppler stops at this page
            )
            logger.info(f"Converted PDF to {len(images)} images at {self.dpi} DPI: {pdf_path}")

            # Standardize image resolution for optimal OCR performance
            target_width = settings.TARGET_IMAGE_WIDTH

            # If target_width is 0, skip resizing
            if target_width == 0:
                logger.info("Image resizing disabled (TARGET_IMAGE_WIDTH = 0)")
                return images

            standardized_images = []

            for idx, img in enumerate(images):
                original_width, original_height = img.size

                # Only resize if image is significantly larger than target (20% threshold)
                if original_width > target_width * 1.2:
                    # Calculate new dimensions maintaining aspect ratio
                    scale_factor = target_width / original_width
                    new_width = target_width
                    new_height = int(original_height * scale_factor)

                    # Use LANCZOS for high-quality downsampling
                    resized_img = img.resize((new_width, new_height), Image.LANCZOS)
                    logger.debug(f"Resized image {idx+1}: {original_width}x{original_height} -> {new_width}x{new_height}")
                    standardized_images.append(resized_img)
                else:
                    # Keep original if already optimal size
                    logger.debug(f"Image {idx+1} kept at original size: {original_width}x{original_height}")
                    standardized_images.append(img)

            logger.info(f"Standardized {len(standardized_images)} images to ~{target_width}px width")
            return standardized_images
        except Exception as e:
            logger.error(f"Error converting PDF to images: {e}")
            raise
    
    def ocr_image(self, image: Image.Image, page_num: int) -> Dict:
        """
        Perform OCR on a single image

        Args:
            image: PIL Image object
            page_num: Page number (for reference)

        Returns:
            Dictionary with page_num and extracted text
        """
        try:
            text = pytesseract.image_to_string(
                image,
                lang=self.lang,
                config=self.tesseract_config
            )
            logger.debug(f"OCR completed for page {page_num}: {len(text)} characters")
            return {
                "page_num": page_num,
                "text": text.strip()
            }
        except Exception as e:
            logger.error(f"OCR error on page {page_num}: {e}")
            return {
                "page_num": page_num,
                "text": "",
                "error": str(e)
            }

    @staticmethod
    def _ocr_image_static(args: tuple) -> Dict:
        """
        Static method for multiprocessing OCR on a single image
        Uses temporary file to avoid pickle errors with large images

        Args:
            args: Tuple of (temp_image_path, page_num, lang, tesseract_config)

        Returns:
            Dictionary with page_num and extracted text
        """
        temp_image_path, page_num, lang, tesseract_config = args
        try:
            # Load image from temporary file
            image = Image.open(temp_image_path)

            text = pytesseract.image_to_string(
                image,
                lang=lang,
                config=tesseract_config
            )

            # Clean up temp file immediately after OCR
            try:
                image.close()
                os.unlink(temp_image_path)
            except:
                pass

            return {
                "page_num": page_num,
                "text": text.strip()
            }
        except Exception as e:
            logger.error(f"OCR error on page {page_num}: {e}")
            # Try to clean up temp file even on error
            try:
                os.unlink(temp_image_path)
            except:
                pass
            return {
                "page_num": page_num,
                "text": "",
                "error": str(e)
            }
    
    def ocr_pdf(self, pdf_path: str, max_pages: int = 25, images: Optional[List[Image.Image]] = None) -> List[Dict]:
        """
        Perform OCR on entire PDF (limited to max_pages)
        Uses multiprocessing if ENABLE_OCR_MULTIPROCESSING is True

        Args:
            pdf_path: Path to PDF file
            max_pages: Maximum pages to process (default: 25)
            images: Pre-converted images (optional). If None, will convert PDF to images.

        Returns:
            List of dictionaries with page_num and text for each page
        """
        try:
            # Use pre-converted images if provided, otherwise convert PDF
            if images is None:
                images = self.pdf_to_images(pdf_path, max_pages=max_pages)

            # Use multiprocessing if enabled and we have multiple pages
            if settings.ENABLE_OCR_MULTIPROCESSING and len(images) > 1:
                results = self._ocr_pdf_multiprocess(images)
            else:
                # Sequential processing (original behavior)
                results = []
                for idx, image in enumerate(images, start=1):
                    result = self.ocr_image(image, idx)
                    results.append(result)

            logger.info(
                f"OCR completed for {pdf_path}: {len(results)} pages processed "
                f"(max: {max_pages}, mode: {'parallel' if settings.ENABLE_OCR_MULTIPROCESSING and len(images) > 1 else 'sequential'})"
            )
            return results

        except Exception as e:
            logger.error(f"Error in OCR PDF processing: {e}")
            raise

    def _ocr_pdf_multiprocess(self, images: List[Image.Image]) -> List[Dict]:
        """
        Process OCR using multiprocessing for faster page-level parallelism
        Saves images to temp files to avoid pickle errors with large images

        Args:
            images: List of PIL Image objects

        Returns:
            List of dictionaries with page_num and text for each page
        """
        num_workers = min(settings.OCR_PAGE_WORKERS, len(images))

        # Save images to temporary files to avoid pickle errors
        temp_files = []
        ocr_args = []

        try:
            for idx, image in enumerate(images, start=1):
                # Create temporary file for this image
                temp_fd, temp_path = tempfile.mkstemp(suffix='.png', prefix=f'ocr_page_{idx}_')
                os.close(temp_fd)  # Close file descriptor immediately

                # Save image to temp file
                image.save(temp_path, 'PNG', optimize=False)
                temp_files.append(temp_path)

                # Prepare args with temp file path instead of image object
                ocr_args.append((temp_path, idx, self.lang, self.tesseract_config))

            # Process with multiprocessing pool
            with Pool(processes=num_workers) as pool:
                results = pool.map(self._ocr_image_static, ocr_args, chunksize=1)

            logger.debug(f"Multiprocessing OCR completed: {len(results)} pages with {num_workers} workers")
            return results

        except Exception as e:
            logger.error(f"Error in multiprocessing OCR: {e}, falling back to sequential")

            # Clean up temp files
            for temp_path in temp_files:
                try:
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                except:
                    pass

            # Fallback to sequential processing
            results = []
            for idx, image in enumerate(images, start=1):
                result = self.ocr_image(image, idx)
                results.append(result)
            return results
    
    def get_full_text(self, pdf_path: str, max_pages: int = 30, return_images: bool = False):
        """
        Get complete OCR text from PDF with page markers (limited to max_pages)

        Args:
            pdf_path: Path to PDF file
            max_pages: Maximum pages to process (default: 30)
            return_images: If True, returns tuple of (text, images). If False, returns only text.

        Returns:
            Complete text with page markers, or tuple of (text, images) if return_images=True
        """
        # Convert PDF to images once
        images = self.pdf_to_images(pdf_path, max_pages=max_pages)

        # Pass the images to ocr_pdf to avoid re-conversion
        results = self.ocr_pdf(pdf_path, max_pages=max_pages, images=images)
        full_text = ""

        for result in results:
            page_num = result.get("page_num", 0)
            text = result.get("text", "")
            full_text += f"\n\n--- Page {page_num} ---\n\n{text}"

        if return_images:
            return full_text.strip(), images
        return full_text.strip()