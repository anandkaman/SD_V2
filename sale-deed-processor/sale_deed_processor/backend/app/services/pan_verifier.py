# backend/app/services/pan_verifier.py

"""
PAN Verifier Service - Extracts and verifies PAN numbers

Extracts PAN numbers from:
1. OCR text using regex pattern
2. Gemini JSON response (buyer/seller/confirming party fields)

Compares counts to detect mismatches and trigger Vision API fallback
"""

import re
import logging
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)


class PANVerifier:
    """Service to extract and verify PAN numbers"""
    
    # PAN format: 5 letters + 4 digits + 1 letter (e.g., ABCDE1234F)
    PAN_PATTERN = r'\b[A-Z]{5}[0-9]{4}[A-Z]\b'
    
    def __init__(self):
        """Initialize PAN Verifier"""
        self.pan_regex = re.compile(self.PAN_PATTERN)
        logger.info("PAN Verifier initialized")
    
    def extract_pans_from_ocr(self, ocr_text: str) -> List[str]:
        """
        Extract all PAN numbers from OCR text
        
        Args:
            ocr_text: OCR text to search for PANs
            
        Returns:
            List of PAN numbers found (may contain duplicates)
        """
        if not ocr_text:
            return []
        
        pans = self.pan_regex.findall(ocr_text)
        
        logger.debug(f"Found {len(pans)} PAN numbers in OCR text")
        if pans:
            logger.debug(f"PANs: {pans}")
        
        return pans
    
    def extract_pans_from_images(self, images: list, ocr_service) -> list[str]:
        """
        Extract PAN numbers from images using Tesseract English-only OCR
        
        This provides a second source of PAN extraction for better accuracy.
        Uses English-only Tesseract for maximum PAN recognition.
        
        Args:
            images: List of PIL Image objects
            ocr_service: OCRService instance for Tesseract OCR
            
        Returns:
            List of PAN numbers found in images (may contain duplicates)
        """
        if not images:
            return []
        
        all_pans = []
        
        try:
            from app.services.ocr_cleaner import OCRCleaner
            cleaner = OCRCleaner()
            
            # Run Tesseract English-only OCR on images
            logger.info(f"Running Tesseract English-only OCR on {len(images)} images for PAN extraction")
            ocr_results = ocr_service.ocr_pdf(
                pdf_path=None,  # Not needed when images provided
                max_pages=len(images),
                images=images
            )
            
            # Extract and clean text from all pages
            for result in ocr_results:
                if result.get('text'):
                    # Clean the OCR text
                    cleaned_text = cleaner.clean_text(result['text'])
                    # Extract PANs
                    page_pans = self.pan_regex.findall(cleaned_text)
                    all_pans.extend(page_pans)
            
            logger.info(f"Tesseract OCR found {len(all_pans)} PAN numbers across {len(images)} images")
            if all_pans:
                logger.debug(f"Tesseract PANs: {all_pans}")
            
            return all_pans
            
        except Exception as e:
            logger.error(f"Error extracting PANs from images: {e}")
            return []
    
    def extract_pans_from_json(self, json_data: Dict) -> List[str]:
        """
        Extract PAN numbers from Gemini JSON response
        
        Searches in:
        - buyer_details[].pan_card_number
        - seller_details[].pan_card_number
        - confirming_party_details[].pan_card_number
        
        Args:
            json_data: Gemini JSON response dictionary
            
        Returns:
            List of PAN numbers found in JSON
        """
        pans = []
        
        # Extract from buyers
        buyers = json_data.get("buyer_details", [])
        for buyer in buyers:
            pan = buyer.get("pan_card_number")
            if pan and isinstance(pan, str) and self.pan_regex.match(pan):
                pans.append(pan)
        
        # Extract from sellers
        sellers = json_data.get("seller_details", [])
        for seller in sellers:
            pan = seller.get("pan_card_number")
            if pan and isinstance(pan, str) and self.pan_regex.match(pan):
                pans.append(pan)
        
        # Extract from confirming parties
        confirming_parties = json_data.get("confirming_party_details", [])
        for party in confirming_parties:
            pan = party.get("pan_card_number")
            if pan and isinstance(pan, str) and self.pan_regex.match(pan):
                pans.append(pan)
        
        logger.debug(f"Found {len(pans)} PAN numbers in JSON response")
        if pans:
            logger.debug(f"PANs: {pans}")
        
        return pans
    
    def get_unique_pans(self, pans: List[str]) -> List[str]:
        """
        Get unique PAN numbers from a list
        
        Args:
            pans: List of PAN numbers (may contain duplicates)
            
        Returns:
            List of unique PAN numbers
        """
        return list(set(pans))
    
    def verify_pan_counts(
        self, 
        ocr_pans: List[str], 
        json_pans: List[str]
    ) -> Tuple[bool, Dict[str, any]]:
        """
        Verify if PAN counts match between OCR and JSON
        
        Args:
            ocr_pans: List of PANs extracted from OCR
            json_pans: List of PANs extracted from JSON
            
        Returns:
            Tuple of (is_match, details_dict)
            - is_match: True if counts match, False otherwise
            - details_dict: Dictionary with verification details
        """
        unique_ocr_pans = self.get_unique_pans(ocr_pans)
        unique_json_pans = self.get_unique_pans(json_pans)
        
        ocr_count = len(unique_ocr_pans)
        json_count = len(unique_json_pans)
        
        is_match = ocr_count == json_count
        
        details = {
            "ocr_pan_count": ocr_count,
            "json_pan_count": json_count,
            "ocr_pans": unique_ocr_pans,
            "json_pans": unique_json_pans,
            "is_match": is_match,
            "missing_in_json": list(set(unique_ocr_pans) - set(unique_json_pans)),
            "extra_in_json": list(set(unique_json_pans) - set(unique_ocr_pans))
        }
        
        if is_match:
            logger.info(f"✓ PAN verification PASSED: {ocr_count} PANs match")
        else:
            logger.warning(
                f"✗ PAN verification FAILED: OCR has {ocr_count} PANs, "
                f"JSON has {json_count} PANs"
            )
            if details["missing_in_json"]:
                logger.warning(f"  Missing in JSON: {details['missing_in_json']}")
            if details["extra_in_json"]:
                logger.warning(f"  Extra in JSON: {details['extra_in_json']}")
        
        return is_match, details
