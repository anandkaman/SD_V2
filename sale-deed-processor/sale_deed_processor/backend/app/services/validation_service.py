# backend/app/services/validation_service.py

import re
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class ValidationService:
    
    @staticmethod
    def validate_aadhaar(aadhaar: str) -> bool:
        """Validate Aadhaar number format (12 digits)"""
        if not aadhaar:
            return False
        cleaned = re.sub(r'[\s-]', '', str(aadhaar))
        return bool(re.match(r'^\d{12}$', cleaned))
    
    @staticmethod
    def validate_pan(pan: str) -> bool:
        """Validate PAN card format (5 letters, 4 digits, 1 letter)"""
        if not pan:
            return False
        cleaned = str(pan).upper().strip()
        return bool(re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', cleaned))
    
    @staticmethod
    def validate_pincode(pincode: str) -> bool:
        """Validate Indian pincode (6 digits)"""
        if not pincode:
            return False
        cleaned = re.sub(r'\s', '', str(pincode))
        return bool(re.match(r'^\d{6}$', cleaned))
    
    @staticmethod
    def validate_registration_fee(fee: float, min_threshold: float = 4000.0) -> bool:
        """Validate registration fee is above minimum threshold"""
        if fee is None:
            return False
        try:
            return float(fee) >= min_threshold
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def clean_aadhaar(aadhaar: str) -> Optional[str]:
        """Clean and format Aadhaar number"""
        if not aadhaar:
            return None
        cleaned = re.sub(r'[\s-]', '', str(aadhaar))
        if re.match(r'^\d{12}$', cleaned):
            return cleaned
        return None
    
    @staticmethod
    def clean_pan(pan: str) -> Optional[str]:
        """Clean and format PAN card"""
        if not pan:
            return None
        cleaned = str(pan).upper().strip()
        if re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', cleaned):
            return cleaned
        return None
    
    @staticmethod
    def clean_pincode(pincode: str) -> Optional[str]:
        """Clean and format pincode"""
        if not pincode:
            return None
        cleaned = re.sub(r'\s', '', str(pincode))
        if re.match(r'^\d{6}$', cleaned):
            return cleaned
        return None
    
    @staticmethod
    def calculate_guidance_value(registration_fee: float) -> float:
        """Calculate guidance value (registration_fee * 100)"""
        try:
            return round(float(registration_fee) * 100, 2)
        except (ValueError, TypeError):
            return 0.0
    
    @staticmethod
    def validate_and_clean_data(extracted_data: Dict) -> Dict:
        """
        Validate and clean all extracted data
        
        Args:
            extracted_data: Raw data from LLM
            
        Returns:
            Cleaned and validated data
        """
        cleaned = {
            "buyer_details": [],
            "seller_details": [],
            "confirming_party_details": [],
            "property_details": {},
            "document_details": {}
        }
        
        # Clean buyer details
        buyers = extracted_data.get("buyer_details", [])
        if not isinstance(buyers, list):
            buyers = [buyers] if buyers else []
        
        for buyer in buyers:
            cleaned_buyer = {
                "name": buyer.get("name"),
                "gender": buyer.get("gender"),
                "father_name": buyer.get("father_name"),
                "date_of_birth": buyer.get("date_of_birth"),
                "aadhaar_number": ValidationService.clean_aadhaar(buyer.get("aadhaar_number")),
                "pan_card_number": ValidationService.clean_pan(buyer.get("pan_card_number")),
                "address": buyer.get("address"),
                "pincode": ValidationService.clean_pincode(buyer.get("pincode")),
                "state": buyer.get("state"),
                "phone_number": buyer.get("phone_number"),
                "secondary_phone_number": buyer.get("secondary_phone_number"),
                "email": buyer.get("email")
            }
            cleaned["buyer_details"].append(cleaned_buyer)
        
        # Clean seller details
        sellers = extracted_data.get("seller_details", [])
        if not isinstance(sellers, list):
            sellers = [sellers] if sellers else []
        
        for seller in sellers:
            cleaned_seller = {
                "name": seller.get("name"),
                "gender": seller.get("gender"),
                "father_name": seller.get("father_name"),
                "date_of_birth": seller.get("date_of_birth"),
                "aadhaar_number": ValidationService.clean_aadhaar(seller.get("aadhaar_number")),
                "pan_card_number": ValidationService.clean_pan(seller.get("pan_card_number")),
                "address": seller.get("address"),
                "pincode": ValidationService.clean_pincode(seller.get("pincode")),
                "state": seller.get("state"),
                "phone_number": seller.get("phone_number"),
                "secondary_phone_number": seller.get("secondary_phone_number"),
                "email": seller.get("email"),
                "property_share": seller.get("property_share")
            }
            cleaned["seller_details"].append(cleaned_seller)
        
        # Clean confirming party details
        confirming_parties = extracted_data.get("confirming_party_details", [])
        if not isinstance(confirming_parties, list):
            confirming_parties = [confirming_parties] if confirming_parties else []
        
        for confirming_party in confirming_parties:
            cleaned_confirming = {
                "name": confirming_party.get("name"),
                "gender": confirming_party.get("gender"),
                "father_name": confirming_party.get("father_name"),
                "date_of_birth": confirming_party.get("date_of_birth"),
                "aadhaar_number": ValidationService.clean_aadhaar(confirming_party.get("aadhaar_number")),
                "pan_card_number": ValidationService.clean_pan(confirming_party.get("pan_card_number")),
                "address": confirming_party.get("address"),
                "pincode": ValidationService.clean_pincode(confirming_party.get("pincode")),
                "state": confirming_party.get("state"),
                "phone_number": confirming_party.get("phone_number"),
                "secondary_phone_number": confirming_party.get("secondary_phone_number"),
                "email": confirming_party.get("email")
            }
            cleaned["confirming_party_details"].append(cleaned_confirming)
        
        # Clean property details (NO registration_fee here)
        prop = extracted_data.get("property_details", {})

        cleaned["property_details"] = {
            "schedule_b_area": prop.get("schedule_b_area"),
            "schedule_c_property_name": prop.get("schedule_c_property_name"),
            "schedule_c_property_address": prop.get("schedule_c_property_address"),
            "schedule_c_property_area": prop.get("schedule_c_property_area"),
            "paid_in_cash_mode": prop.get("paid_in_cash_mode"),
            "pincode": ValidationService.clean_pincode(prop.get("pincode")),
            "state": prop.get("state"),
            "sale_consideration": prop.get("sale_consideration"),
            "stamp_duty_fee": prop.get("stamp_duty_fee"),
            "registration_fee": None,  # Will be set by pdfplumber or vision model
            "guidance_value": None,    # Will be calculated after registration_fee is set
            "remarks": prop.get("remarks")  # NEW: Preserve remarks
        }
        
        # Clean document details
        doc = extracted_data.get("document_details", {})
        cleaned["document_details"] = {
            "transaction_date": doc.get("transaction_date"),
            "registration_office": doc.get("registration_office")
        }
        
        logger.info(f"Data validation complete: {len(cleaned['buyer_details'])} buyers, {len(cleaned['seller_details'])} sellers, {len(cleaned['confirming_party_details'])} confirming parties")
        
        return cleaned