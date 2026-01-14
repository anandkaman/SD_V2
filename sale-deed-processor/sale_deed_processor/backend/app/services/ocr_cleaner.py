# backend/app/services/ocr_cleaner.py

"""
OCR Cleaner Service - Filters OCR text to keep only relevant characters

Preserves:
- Kannada Unicode range: U+0C80 to U+0CFF
- English letters: A-Z, a-z
- Numbers: 0-9
- Symbols: , . - and space
- Newlines (to preserve document structure)

Removes all other characters (unwanted symbols, other scripts, etc.)
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class OCRCleaner:
    """Service to clean OCR text by filtering unwanted characters"""
    
    # Unicode ranges and allowed characters
    KANNADA_START = 0x0C80
    KANNADA_END = 0x0CFF
    ENGLISH_UPPER_START = 0x0041  # A
    ENGLISH_UPPER_END = 0x005A    # Z
    ENGLISH_LOWER_START = 0x0061  # a
    ENGLISH_LOWER_END = 0x007A    # z
    DIGIT_START = 0x0030          # 0
    DIGIT_END = 0x0039            # 9
    ALLOWED_SYMBOLS = {',', '.', '-', ' ', '\n', '\r'}
    
    def __init__(self):
        """Initialize OCR Cleaner"""
        logger.info("OCR Cleaner initialized")
    
    def is_allowed_character(self, char: str) -> bool:
        """
        Check if a character should be kept
        
        Args:
            char: Single character to check
            
        Returns:
            True if character should be kept, False otherwise
        """
        if char in self.ALLOWED_SYMBOLS:
            return True
        
        char_code = ord(char)
        
        # Check Kannada range
        if self.KANNADA_START <= char_code <= self.KANNADA_END:
            return True
        
        # Check English uppercase
        if self.ENGLISH_UPPER_START <= char_code <= self.ENGLISH_UPPER_END:
            return True
        
        # Check English lowercase
        if self.ENGLISH_LOWER_START <= char_code <= self.ENGLISH_LOWER_END:
            return True
        
        # Check digits
        if self.DIGIT_START <= char_code <= self.DIGIT_END:
            return True
        
        return False
    
    def clean_text(self, text: str) -> str:
        """
        Clean OCR text by filtering unwanted characters
        
        Args:
            text: Raw OCR text to clean
            
        Returns:
            Cleaned text with only allowed characters
        """
        if not text:
            return ""
        
        original_length = len(text)
        
        # Filter characters
        cleaned = ''.join(char for char in text if self.is_allowed_character(char))
        
        cleaned_length = len(cleaned)
        reduction_pct = 100 * (original_length - cleaned_length) / original_length if original_length > 0 else 0
        
        logger.info(
            f"OCR cleaning complete: {original_length} → {cleaned_length} chars "
            f"({reduction_pct:.1f}% reduction)"
        )
        
        return cleaned
    
    def clean_text_from_file(self, file_path: str, output_path: Optional[str] = None) -> str:
        """
        Clean OCR text from a file
        
        Args:
            file_path: Path to file containing OCR text
            output_path: Optional path to save cleaned text
            
        Returns:
            Cleaned text
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            cleaned = self.clean_text(text)
            
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(cleaned)
                logger.info(f"Cleaned OCR saved to: {output_path}")
            
            return cleaned
            
        except Exception as e:
            logger.error(f"Error cleaning OCR from file {file_path}: {e}")
            raise
