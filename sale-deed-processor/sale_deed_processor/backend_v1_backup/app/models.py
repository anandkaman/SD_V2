# backend/app/models.py

from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class DocumentDetail(Base):
    __tablename__ = "document_details"
    
    document_id = Column(String, primary_key=True, index=True)
    transaction_date = Column(Date, nullable=True)
    registration_office = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    property_details = relationship("PropertyDetail", back_populates="document", uselist=False)
    sellers = relationship("SellerDetail", back_populates="document")
    buyers = relationship("BuyerDetail", back_populates="document")

class PropertyDetail(Base):
    __tablename__ = "property_details"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String, ForeignKey("document_details.document_id"), unique=True)
    total_land_area = Column(Float, nullable=True)
    address = Column(String, nullable=True)
    pincode = Column(String, nullable=True)
    state = Column(String, nullable=True)
    sale_consideration = Column(String, nullable=True)  # Changed from Float to String to support formatted values like "Rs.28,62,413/-"
    stamp_duty_fee = Column(String, nullable=True)  # Changed from Float to String
    registration_fee = Column(String, nullable=True)  # Changed from Float to String
    guidance_value = Column(String, nullable=True)  # Changed from Float to String
    
    document = relationship("DocumentDetail", back_populates="property_details")

class SellerDetail(Base):
    __tablename__ = "seller_details"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String, ForeignKey("document_details.document_id"))
    name = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    aadhaar_number = Column(String, nullable=True)
    pan_card_number = Column(String, nullable=True)
    address = Column(String, nullable=True)
    pincode = Column(String, nullable=True)
    state = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    secondary_phone_number = Column(String, nullable=True)
    email = Column(String, nullable=True)
    property_share = Column(String, nullable=True)
    
    document = relationship("DocumentDetail", back_populates="sellers")

class BuyerDetail(Base):
    __tablename__ = "buyer_details"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String, ForeignKey("document_details.document_id"))
    name = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    aadhaar_number = Column(String, nullable=True)
    pan_card_number = Column(String, nullable=True)
    address = Column(String, nullable=True)
    pincode = Column(String, nullable=True)
    state = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    secondary_phone_number = Column(String, nullable=True)
    email = Column(String, nullable=True)
    
    document = relationship("DocumentDetail", back_populates="buyers")