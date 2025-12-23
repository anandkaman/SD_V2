# backend/app/schemas.py

from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List
from datetime import date, datetime
import re

def parse_currency_string(value):
    """Convert currency strings like 'Rs. 22,67,565/-' to float"""
    if isinstance(value, (int, float)):
        return float(value)
    if value is None:
        return None
    if isinstance(value, str):
        # Remove 'Rs.', '/-', spaces, and commas
        cleaned = re.sub(r'[Rs./\-,\s]', '', value)
        if cleaned:
            try:
                return float(cleaned)
            except ValueError:
                return None
    return None

class BuyerDetailSchema(BaseModel):
    id: int
    document_id: str
    name: Optional[str] = None
    gender: Optional[str] = None
    aadhaar_number: Optional[str] = None
    pan_card_number: Optional[str] = None
    address: Optional[str] = None
    pincode: Optional[str] = None
    state: Optional[str] = None
    phone_number: Optional[str] = None
    secondary_phone_number: Optional[str] = None
    email: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class SellerDetailSchema(BaseModel):
    id: int
    document_id: str
    name: Optional[str] = None
    gender: Optional[str] = None
    aadhaar_number: Optional[str] = None
    pan_card_number: Optional[str] = None
    address: Optional[str] = None
    pincode: Optional[str] = None
    state: Optional[str] = None
    phone_number: Optional[str] = None
    secondary_phone_number: Optional[str] = None
    email: Optional[str] = None
    property_share: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class PropertyDetailSchema(BaseModel):
    id: int
    document_id: str
    total_land_area: Optional[float] = None
    address: Optional[str] = None
    pincode: Optional[str] = None
    state: Optional[str] = None
    sale_consideration: Optional[float] = None
    stamp_duty_fee: Optional[float] = None
    registration_fee: Optional[float] = None
    guidance_value: Optional[float] = None
    
    @field_validator('sale_consideration', 'stamp_duty_fee', 'registration_fee', 'guidance_value', 'total_land_area', mode='before')
    @classmethod
    def parse_numeric_fields(cls, v):
        return parse_currency_string(v)
    
    model_config = ConfigDict(from_attributes=True)

class DocumentDetailSchema(BaseModel):
    document_id: str
    transaction_date: Optional[date] = None
    registration_office: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    property_details: Optional[PropertyDetailSchema] = None
    buyers: List[BuyerDetailSchema] = []
    sellers: List[SellerDetailSchema] = []
    
    model_config = ConfigDict(from_attributes=True)

class ProcessingStatsSchema(BaseModel):
    total: int
    processed: int
    successful: int
    failed: int
    is_running: bool = False
    active_workers: int = 0
    current_file: Optional[str] = None

class BatchResultSchema(BaseModel):
    document_id: str
    status: str
    registration_fee: Optional[float] = None
    llm_extracted: bool
    saved_to_db: bool
    error: Optional[str] = None

class SystemInfoSchema(BaseModel):
    cuda_available: bool
    cuda_device_count: int
    poppler_available: bool
    tesseract_available: bool
    ollama_connected: bool
    yolo_model_loaded: bool