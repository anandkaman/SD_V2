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
    father_name: Optional[str] = None
    date_of_birth: Optional[date] = None
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
    father_name: Optional[str] = None
    date_of_birth: Optional[date] = None
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

class ConfirmingPartyDetailSchema(BaseModel):
    id: int
    document_id: str
    name: Optional[str] = None
    gender: Optional[str] = None
    father_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    aadhaar_number: Optional[str] = None
    pan_card_number: Optional[str] = None
    address: Optional[str] = None
    pincode: Optional[str] = None
    state: Optional[str] = None
    phone_number: Optional[str] = None
    secondary_phone_number: Optional[str] = None
    email: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class PropertyDetailSchema(BaseModel):
    id: int
    document_id: str
    schedule_b_area: Optional[float] = None
    schedule_c_property_name: Optional[str] = None
    schedule_c_property_address: Optional[str] = None
    schedule_c_property_area: Optional[float] = None
    paid_in_cash_mode: Optional[str] = None
    pincode: Optional[str] = None
    state: Optional[str] = None
    sale_consideration: Optional[float] = None
    stamp_duty_fee: Optional[float] = None
    registration_fee: Optional[float] = None
    guidance_value: Optional[float] = None

    @field_validator('sale_consideration', 'stamp_duty_fee', 'registration_fee', 'guidance_value', 'schedule_b_area', 'schedule_c_property_area', mode='before')
    @classmethod
    def parse_numeric_fields(cls, v):
        return parse_currency_string(v)

    model_config = ConfigDict(from_attributes=True)

class DocumentDetailSchema(BaseModel):
    document_id: str
    batch_id: Optional[str] = None
    transaction_date: Optional[date] = None
    registration_office: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    property_details: Optional[PropertyDetailSchema] = None
    buyers: List[BuyerDetailSchema] = []
    sellers: List[SellerDetailSchema] = []
    confirming_parties: List[ConfirmingPartyDetailSchema] = []

    model_config = ConfigDict(from_attributes=True)

class ProcessingStatsSchema(BaseModel):
    total: int
    processed: int
    successful: int
    failed: int
    is_running: bool = False
    active_workers: int = 0
    current_file: Optional[str] = None
    # Pipeline-specific fields (V2)
    ocr_workers: Optional[int] = None
    llm_workers: Optional[int] = None
    ocr_active: Optional[int] = None
    llm_active: Optional[int] = None
    in_queue: Optional[int] = None
    pipeline_mode: Optional[bool] = None

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


# ✅ NEW SCHEMA: User Info
class UserInfoCreateSchema(BaseModel):
    user_name: str
    number_of_files: int
    file_region: str
    batch_id: Optional[str] = None


class UserInfoSchema(BaseModel):
    id: int
    user_name: str
    number_of_files: int
    file_region: str
    date: datetime
    batch_id: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ✅ NEW SCHEMA: User Tickets
class UserTicketCreateSchema(BaseModel):
    user_name: str
    batch_id: Optional[str] = None
    error_type: str
    description: str


class UserTicketSchema(BaseModel):
    id: int
    user_name: str
    batch_id: Optional[str] = None
    error_type: str
    description: str
    status: str
    created_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)