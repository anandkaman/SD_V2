# backend/app/schemas/document_schemas.py

"""
Pydantic schemas for document data validation and serialization
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


# ===== PROPERTY DETAIL SCHEMAS =====

class PropertyDetailSchema(BaseModel):
    schedule_b_area: Optional[float] = None
    schedule_c_property_name: Optional[str] = None
    schedule_c_property_address: Optional[str] = None
    schedule_c_property_area: Optional[float] = None
    paid_in_cash_mode: Optional[str] = None
    pincode: Optional[str] = None
    state: Optional[str] = None
    sale_consideration: Optional[str] = None
    stamp_duty_fee: Optional[str] = None
    registration_fee: Optional[str] = None
    new_ocr_reg_fee: Optional[str] = None
    guidance_value: Optional[str] = None

    class Config:
        from_attributes = True


# ===== SELLER DETAIL SCHEMAS =====

class SellerDetailSchema(BaseModel):
    name: Optional[str] = None
    fathers_name: Optional[str] = None
    age: Optional[int] = None
    aadhaar: Optional[str] = None
    pan: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True


# ===== BUYER DETAIL SCHEMAS =====

class BuyerDetailSchema(BaseModel):
    name: Optional[str] = None
    fathers_name: Optional[str] = None
    age: Optional[int] = None
    aadhaar: Optional[str] = None
    pan: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True


# ===== CONFIRMING PARTY DETAIL SCHEMAS =====

class ConfirmingPartyDetailSchema(BaseModel):
    name: Optional[str] = None
    fathers_name: Optional[str] = None
    age: Optional[int] = None
    aadhaar: Optional[str] = None
    pan: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True


# ===== DOCUMENT DETAIL SCHEMAS =====

class DocumentDetailResponse(BaseModel):
    """Complete document with all related data"""
    document_id: str
    batch_id: Optional[str] = None
    file_hash: Optional[str] = None
    transaction_date: Optional[date] = None
    registration_office: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Related data
    property_details: Optional[PropertyDetailSchema] = None
    sellers: List[SellerDetailSchema] = []
    buyers: List[BuyerDetailSchema] = []
    confirming_parties: List[ConfirmingPartyDetailSchema] = []

    class Config:
        from_attributes = True


class DocumentUpdateRequest(BaseModel):
    """Request schema for updating document data"""
    # Document fields
    transaction_date: Optional[str] = None
    registration_office: Optional[str] = None
    
    # Property fields
    property: Optional[PropertyDetailSchema] = None
    
    # Party fields (will replace existing)
    sellers: Optional[List[SellerDetailSchema]] = None
    buyers: Optional[List[BuyerDetailSchema]] = None
    confirming_parties: Optional[List[ConfirmingPartyDetailSchema]] = None
    
    # Metadata
    updated_by: Optional[str] = Field(None, description="User who made the update")
    update_reason: Optional[str] = Field(None, description="Reason for update")


class DocumentUpdateResponse(BaseModel):
    """Response after updating document"""
    success: bool
    message: str
    document_id: str
    updated_fields: List[str] = []
    timestamp: datetime

    class Config:
        from_attributes = True
