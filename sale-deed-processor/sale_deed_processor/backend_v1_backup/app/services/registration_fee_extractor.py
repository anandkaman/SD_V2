# backend/app/services/registration_fee_extractor.py

import pdfplumber
import re
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class RegistrationFeeExtractor:
    def __init__(self, threshold_pct=0.7, max_misc_fee=4000.0, min_fee=4000.0):
        self.threshold_pct = threshold_pct
        self.max_misc_fee = max_misc_fee
        self.min_fee = min_fee
        
    def validate_table_numbers(self, numbers):
        """Allow 2 to 5 distinct numeric values as valid."""
        try:
            distinct_values = set(map(float, numbers))
        except ValueError:
            return False, False

        count = len(distinct_values)
        if 2 <= count <= 5:
            return True, False
        elif count > 5:
            return False, True
        else:
            return False, False

    def extract_ordered_numbers_from_page(self, page):
        """Extracts numbers and sorts them by vertical position (Top to Bottom)."""
        words = page.extract_words()
        
        currency_re = re.compile(r"^\d{2,7}\.\d{2}$")
        time_re = re.compile(r"\d{1,2}[:.]\d{2}")

        found_numbers = []

        for w in words:
            text = w['text']

            # Filter out timestamps (e.g., 03.02) - pass but don't skip yet
            if time_re.search(text):
                pass

            clean_text = re.sub(r"[^\d.]", "", text)
            
            if currency_re.match(clean_text):
                try:
                    val = float(clean_text)
                    found_numbers.append((w['top'], val, clean_text))
                except ValueError:
                    continue

        found_numbers.sort(key=lambda x: x[0])
        return [str(x[2]) for x in found_numbers]

    def post_process_registration_fee(self, numbers_ordered):
        """
        Process extracted numbers to find registration fee.
        numbers_ordered: List of strings, sorted physically from Top to Bottom of the page.
        """
        if len(numbers_ordered) < 2:
            return None

        try:
            # Keep order!
            vals = list(map(float, numbers_ordered))
        except ValueError:
            return None

        # Physically First Value (Top of Table)
        first_row_val = vals[0]

        # Max Value (The true arithmetic total found)
        max_val = max(vals)

        # Calculate Sum of Misc (All items <= 4000)
        misc_fees = [v for v in vals if v <= self.max_misc_fee]
        sum_misc_fees = sum(misc_fees)

        logger.debug(f"Ordered Values (Top->Bottom): {vals}")
        logger.debug(f"Top Row Candidate: {first_row_val}")

        final_reg_fee = None

        # --- LOGIC BRANCH 1: CHECK FIRST ROW (Top Value) ---
        # If the physically first number is a valid Fee (> 4000), we prioritize it.
        if first_row_val >= self.min_fee:

            # Verify Ratio against the Max Value found (Total)
            # If first_row IS the max (because Total is missing), ratio is 1.0.
            ratio = first_row_val / max_val if max_val != 0 else 0

            if ratio >= self.threshold_pct:
                logger.info(f"*** Match Found: Top Row ({first_row_val}) is valid (Ratio {ratio:.2f}). ***")
                final_reg_fee = first_row_val
            else:
                # This happens if Top Row is large, but there is an even HUGE total (unlikely for Reg Fee)
                # But if Ratio is bad, we might default to subtraction.
                # However, user said "Never touch first value" if it's the Reg Value.
                # If it passes the size check (>4000), we trust it unless it's clearly a sub-total.
                # For now, we trust the user's direction: if First Row is grabbed and looks fine, keep it.
                logger.info(f"*** Top Row ({first_row_val}) is valid size. Keeping it despite ratio. ***")
                final_reg_fee = first_row_val

        # --- LOGIC BRANCH 2: SUBTRACTION (Fallback) ---
        # If Top Value was small (< 4000) (e.g., Misc Fee), or invalid...
        else:
            logger.info(f"*** Top Row ({first_row_val}) is small/invalid. Switching to Subtraction Mode. ***")
            logger.debug(f"Using Max Value (Total): {max_val}")

            # Subtraction: Total - Sum(Misc)
            # Note: If max_val is actually the Reg Fee (and we missed the real Total),
            # and we didn't catch it in Branch 1 (because it wasn't at the top?),
            # this calculation might run.
            # But in your specific case, '20400' IS at the top, so Branch 1 will catch it.

            # Ensure we don't subtract the Max Value from itself if it was somehow caught in misc (unlikely due to threshold)
            real_misc_sum = sum([v for v in misc_fees if v != max_val])

            calculated_val = max_val - real_misc_sum
            logger.debug(f"Calculation: {max_val} - {real_misc_sum} = {calculated_val}")
            final_reg_fee = calculated_val

        # --- FINAL THRESHOLD CHECK ---
        if final_reg_fee is not None:
            if final_reg_fee < self.min_fee:
                logger.warning(f"Warning: Final Result {final_reg_fee:.2f} is below {self.min_fee}. Discarding.")
                return None

            return float(round(final_reg_fee, 2))

        return None

    def extract(self, pdf_path: str) -> Optional[float]:
        """Extract registration fee from PDF."""
        if not os.path.exists(pdf_path):
            logger.error(f"PDF not found: {pdf_path}")
            return None

        try:
            with pdfplumber.open(pdf_path) as pdf:
                page_num = 2  # Start from page 2 (index 2) like reg_fee_plumber
                max_page = min(len(pdf.pages), page_num + 4)
                
                while page_num < max_page:
                    page = pdf.pages[page_num]
                    logger.debug(f"Processing Page {page_num+1} for table extraction.")

                    numbers = self.extract_ordered_numbers_from_page(page)
                    
                    if not numbers:
                        logger.debug(f"Page {page_num+1} yielded no currency numbers.")
                        page_num += 1
                        continue

                    is_valid, try_next = self.validate_table_numbers(numbers)

                    if is_valid:
                        reg_fee = self.post_process_registration_fee(numbers)
                        
                        if reg_fee is not None:
                            logger.info(f"Registration Fee extracted from page {page_num+1}: {reg_fee}")
                            return reg_fee
                        else:
                            page_num += 1
                            continue
                    elif try_next:
                        logger.debug(f"Page {page_num+1} has too much noise. Trying next page.")
                        page_num += 1
                        continue
                    else:
                        logger.debug(f"Page {page_num+1} invalid data. Stopping.")
                        break

            logger.warning("Registration fee not found in PDF")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting registration fee: {e}")
            return None