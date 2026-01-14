# backend/app/models.py

from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class DocumentDetail(Base):
    __tablename__ = "document_details"
    
    document_id = Column(String, primary_key=True, index=True)
    batch_id = Column(String(100), index=True, nullable=True)  # ✅ ADD THIS LINE
    file_hash = Column(String(64), index=True, nullable=True)  # ✅ SHA256 hash for duplicate detection
    transaction_date = Column(Date, nullable=True)
    registration_office = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    property_details = relationship("PropertyDetail", back_populates="document", uselist=False)
    sellers = relationship("SellerDetail", back_populates="document")
    buyers = relationship("BuyerDetail", back_populates="document")
    confirming_parties = relationship("ConfirmingPartyDetail", back_populates="document")


class PropertyDetail(Base):
    __tablename__ = "property_details"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String, ForeignKey("document_details.document_id"), unique=True)
    schedule_b_area = Column(Float, nullable=True)  # Schedule B area in sq.feet
    schedule_c_property_name = Column(String, nullable=True)  # Schedule C property name
    schedule_c_property_address = Column(String, nullable=True)  # Schedule C property address
    schedule_c_property_area = Column(Float, nullable=True)  # Schedule C property area in sq.feet
    paid_in_cash_mode = Column(String, nullable=True)  # Payment mode (cash)
    pincode = Column(String, nullable=True)
    state = Column(String, nullable=True)
    sale_consideration = Column(String, nullable=True)  # Changed from Float to String to support formatted values like "Rs.28,62,413/-"
    stamp_duty_fee = Column(String, nullable=True)  # Changed from Float to String
    registration_fee = Column(String, nullable=True)  # Changed from Float to String (from pdfplumber)
    new_ocr_reg_fee = Column(String, nullable=True)  # Registration fee extracted from OCR text
    guidance_value = Column(String, nullable=True)  # Changed from Float to String
    remarks = Column(String, nullable=True)  # NEW: Store PAN mismatch and other remarks

    document = relationship("DocumentDetail", back_populates="property_details")


class SellerDetail(Base):
    __tablename__ = "seller_details"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String, ForeignKey("document_details.document_id"))
    name = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    father_name = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=True)
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
    father_name = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    aadhaar_number = Column(String, nullable=True)
    pan_card_number = Column(String, nullable=True)
    address = Column(String, nullable=True)
    pincode = Column(String, nullable=True)
    state = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    secondary_phone_number = Column(String, nullable=True)
    email = Column(String, nullable=True)
    
    document = relationship("DocumentDetail", back_populates="buyers")


class ConfirmingPartyDetail(Base):
    __tablename__ = "confirming_party_details"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String, ForeignKey("document_details.document_id"))
    name = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    father_name = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    aadhaar_number = Column(String, nullable=True)
    pan_card_number = Column(String, nullable=True)
    address = Column(String, nullable=True)
    pincode = Column(String, nullable=True)
    state = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    secondary_phone_number = Column(String, nullable=True)
    email = Column(String, nullable=True)
    
    document = relationship("DocumentDetail", back_populates="confirming_parties")


# ✅ ADD THIS NEW MODEL
class BatchSession(Base):
    __tablename__ = "batch_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)  # Upload time
    processing_started_at = Column(DateTime, nullable=True, index=True)  # Processing start time
    uploaded_count = Column(Integer, default=0)
    processed_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    batch_name = Column(String(200), nullable=True)  # First document name
    status = Column(String(50), default='pending')  # pending, processing, completed


# ✅ NEW MODEL: User Info
class UserInfo(Base):
    __tablename__ = "user_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(200), nullable=False)
    number_of_files = Column(Integer, nullable=False)
    file_region = Column(String(200), nullable=False)  # e.g., Hebbal, Chintamani, Goa
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    batch_id = Column(String(100), nullable=True, index=True)  # Link to batch session
    created_at = Column(DateTime, default=datetime.utcnow)


# ✅ NEW MODEL: User Tickets
class UserTicket(Base):
    __tablename__ = "user_tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(200), nullable=False)
    batch_id = Column(String(100), nullable=True, index=True)  # Link to batch session
    error_type = Column(String(200), nullable=False)
    description = Column(String, nullable=False)  # Text area content
    status = Column(String(50), default='open')  # open, in_progress, resolved, closed
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

#  NEW MODEL: In-App Notifications
class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    message = Column(String, nullable=False)
    notification_type = Column(String(50), default='info')  # success, info, warning, error
    related_id = Column(String(100), nullable=True)  # batch_id, ticket_id, etc.
    related_type = Column(String(50), nullable=True)  # batch, ticket, document, etc.
    is_read = Column(Integer, default=0)  # 0 = unread, 1 = read
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    read_at = Column(DateTime, nullable=True)


#  NEW MODEL: Audit Trail
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_email = Column(String(200), nullable=True)  # Who performed the action
    action_type = Column(String(100), nullable=False)  # create, update, delete, export, etc.
    entity_type = Column(String(100), nullable=False)  # document, batch, ticket, etc.
    entity_id = Column(String(200), nullable=True)  # ID of the affected entity
    action_details = Column(String, nullable=True)  # JSON string with details
    ip_address = Column(String(50), nullable=True)  # User's IP address
    user_agent = Column(String(500), nullable=True)  # Browser/client info
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    success = Column(Integer, default=1)  # 1 = success, 0 = failure
    error_message = Column(String, nullable=True)  # Error details if failed
