# SaleDeed Processor - Database Schema Design v1.0

**Database**: PostgreSQL 13+
**ORM**: SQLAlchemy 2.0.25
**Migration Tool**: Alembic 1.13.1

**Last Updated**: December 2024

## Table of Contents

1. [Overview](#overview)
2. [Database Architecture](#database-architecture)
3. [Table Schemas](#table-schemas)
4. [Relationships & Foreign Keys](#relationships--foreign-keys)
5. [Indexes](#indexes)
6. [Data Types & Constraints](#data-types--constraints)
7. [Entity Relationship Diagram](#entity-relationship-diagram)
8. [Migration Strategy](#migration-strategy)
9. [Performance Optimization](#performance-optimization)
10. [Backup & Recovery](#backup--recovery)

---

## Overview

### Database Purpose
The SaleDeed Processor database stores:
- **Document Metadata**: Transaction details, registration info
- **Property Information**: Land area, address, financial details
- **Buyer/Seller Details**: Personal information, contact details
- **Batch Tracking**: Upload sessions and processing status
- **User Management**: User info and support tickets

### Design Principles
- **Normalization**: 3NF (Third Normal Form) to reduce redundancy
- **Relationships**: One-to-One, One-to-Many with cascading deletes
- **Flexibility**: Nullable fields for optional data
- **Scalability**: Indexed foreign keys for fast lookups
- **Audit Trail**: Created/updated timestamps on all tables

---

## Database Architecture

### Database Connection
```python
DATABASE_URL = "postgresql://postgres:admin@localhost:5432/sale_deed_db"
```

### Connection Pool Settings
- **Pool Size**: 5 connections
- **Max Overflow**: 10 connections
- **Pool Recycle**: 3600 seconds (1 hour)
- **Echo**: False (production), True (development)

---

## Table Schemas

### 1. document_details

**Purpose**: Store core document information and transaction metadata

**Table Definition**:
```sql
CREATE TABLE document_details (
    document_id VARCHAR PRIMARY KEY,
    batch_id VARCHAR(100),
    transaction_date DATE,
    registration_office VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**SQLAlchemy Model**:
```python
class DocumentDetail(Base):
    __tablename__ = "document_details"

    document_id = Column(String, primary_key=True, index=True)
    batch_id = Column(String(100), index=True, nullable=True)
    transaction_date = Column(Date, nullable=True)
    registration_office = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Columns**:

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| document_id | VARCHAR | No | - | **Primary Key**. Unique document identifier (extracted from filename) |
| batch_id | VARCHAR(100) | Yes | NULL | Foreign key to batch_sessions.batch_id |
| transaction_date | DATE | Yes | NULL | Date of property transaction |
| registration_office | VARCHAR | Yes | NULL | Sub-registrar office name |
| created_at | TIMESTAMP | No | CURRENT_TIMESTAMP | Record creation timestamp |
| updated_at | TIMESTAMP | No | CURRENT_TIMESTAMP | Last update timestamp (auto-updated) |

**Indexes**:
- PRIMARY KEY on `document_id`
- INDEX on `batch_id`

**Relationships**:
- **property_details**: One-to-One (1 document → 1 property)
- **buyers**: One-to-Many (1 document → N buyers)
- **sellers**: One-to-Many (1 document → N sellers)

**Sample Data**:
```sql
INSERT INTO document_details (document_id, batch_id, transaction_date, registration_office)
VALUES ('DOC_2024_001', 'BATCH_20241223_130000_a1b2c3d4', '2024-01-15', 'Sub-Registrar Office, Bangalore');
```

---

### 2. property_details

**Purpose**: Store property-specific information including financial details

**Table Definition**:
```sql
CREATE TABLE property_details (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR UNIQUE REFERENCES document_details(document_id) ON DELETE CASCADE,
    schedule_b_area FLOAT,
    schedule_c_property_name VARCHAR,
    schedule_c_property_address VARCHAR,
    schedule_c_property_area FLOAT,
    paid_in_cash_mode VARCHAR,
    pincode VARCHAR,
    state VARCHAR,
    sale_consideration VARCHAR,
    stamp_duty_fee VARCHAR,
    registration_fee VARCHAR,
    new_ocr_reg_fee VARCHAR,
    guidance_value VARCHAR
);
```

**SQLAlchemy Model**:
```python
class PropertyDetail(Base):
    __tablename__ = "property_details"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String, ForeignKey("document_details.document_id"), unique=True)
    schedule_b_area = Column(Float, nullable=True)
    schedule_c_property_name = Column(String, nullable=True)
    schedule_c_property_address = Column(String, nullable=True)
    schedule_c_property_area = Column(Float, nullable=True)
    paid_in_cash_mode = Column(String, nullable=True)
    pincode = Column(String, nullable=True)
    state = Column(String, nullable=True)
    sale_consideration = Column(String, nullable=True)
    stamp_duty_fee = Column(String, nullable=True)
    registration_fee = Column(String, nullable=True)
    new_ocr_reg_fee = Column(String, nullable=True)
    guidance_value = Column(String, nullable=True)
```

**Columns**:

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | INTEGER | No | **Primary Key**. Auto-increment |
| document_id | VARCHAR | No | **Foreign Key** to document_details.document_id. **UNIQUE constraint** (one-to-one) |
| schedule_b_area | FLOAT | Yes | Schedule B land area in sq. feet |
| schedule_c_property_name | VARCHAR | Yes | Schedule C property name/type |
| schedule_c_property_address | VARCHAR | Yes | Schedule C property address |
| schedule_c_property_area | FLOAT | Yes | Schedule C property area in sq. feet |
| paid_in_cash_mode | VARCHAR | Yes | Payment mode (cash/cheque/online) |
| pincode | VARCHAR | Yes | Property location pincode |
| state | VARCHAR | Yes | Property state |
| sale_consideration | VARCHAR | Yes | Sale amount (stored as string to preserve formatting) |
| stamp_duty_fee | VARCHAR | Yes | Stamp duty amount |
| registration_fee | VARCHAR | Yes | Registration fee (from pdfplumber) |
| new_ocr_reg_fee | VARCHAR | Yes | Registration fee (from OCR/vision) |
| guidance_value | VARCHAR | Yes | Government guidance value |

**Design Notes**:
- **Monetary Fields as VARCHAR**: Stored as strings to preserve original formatting (e.g., "Rs. 28,62,413/-")
- **Dual Registration Fee Fields**:
  - `registration_fee`: Extracted from PDF tables via pdfplumber
  - `new_ocr_reg_fee`: Extracted from vision model for validation

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE INDEX on `document_id`

**Foreign Keys**:
- `document_id` → `document_details.document_id` (ON DELETE CASCADE)

**Sample Data**:
```sql
INSERT INTO property_details (document_id, schedule_b_area, schedule_c_property_address,
    sale_consideration, stamp_duty_fee, registration_fee)
VALUES ('DOC_2024_001', 1200.0, '123, MG Road, Bangalore',
    'Rs. 50,00,000/-', 'Rs. 2,50,000/-', 'Rs. 50,000/-');
```

---

### 3. seller_details

**Purpose**: Store seller personal and contact information

**Table Definition**:
```sql
CREATE TABLE seller_details (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR REFERENCES document_details(document_id) ON DELETE CASCADE,
    name VARCHAR,
    gender VARCHAR,
    aadhaar_number VARCHAR,
    pan_card_number VARCHAR,
    address VARCHAR,
    pincode VARCHAR,
    state VARCHAR,
    phone_number VARCHAR,
    secondary_phone_number VARCHAR,
    email VARCHAR,
    property_share VARCHAR
);
```

**SQLAlchemy Model**:
```python
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
```

**Columns**:

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | INTEGER | No | **Primary Key**. Auto-increment |
| document_id | VARCHAR | No | **Foreign Key** to document_details.document_id |
| name | VARCHAR | Yes | Seller full name |
| gender | VARCHAR | Yes | Seller gender (Male/Female/Other) |
| aadhaar_number | VARCHAR | Yes | Aadhaar number (12 digits) |
| pan_card_number | VARCHAR | Yes | PAN card number (10 characters) |
| address | VARCHAR | Yes | Full residential address |
| pincode | VARCHAR | Yes | Address pincode |
| state | VARCHAR | Yes | Seller state |
| phone_number | VARCHAR | Yes | Primary phone number |
| secondary_phone_number | VARCHAR | Yes | Secondary/alternate phone |
| email | VARCHAR | Yes | Email address |
| property_share | VARCHAR | Yes | Seller's share in property (e.g., "50%", "1/3") |

**Design Notes**:
- **One-to-Many**: Multiple sellers can be associated with one document
- **No UNIQUE Constraint**: Same seller can appear in multiple documents
- **Property Share**: Unique to sellers (not present in buyers table)

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `document_id` (implicit from foreign key)

**Foreign Keys**:
- `document_id` → `document_details.document_id` (ON DELETE CASCADE)

**Sample Data**:
```sql
INSERT INTO seller_details (document_id, name, gender, aadhaar_number, pan_card_number, property_share)
VALUES ('DOC_2024_001', 'Suresh Sharma', 'Male', '2345-6789-0123', 'FGHIJ5678K', '100%');
```

---

### 4. buyer_details

**Purpose**: Store buyer personal and contact information

**Table Definition**:
```sql
CREATE TABLE buyer_details (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR REFERENCES document_details(document_id) ON DELETE CASCADE,
    name VARCHAR,
    gender VARCHAR,
    aadhaar_number VARCHAR,
    pan_card_number VARCHAR,
    address VARCHAR,
    pincode VARCHAR,
    state VARCHAR,
    phone_number VARCHAR,
    secondary_phone_number VARCHAR,
    email VARCHAR
);
```

**SQLAlchemy Model**:
```python
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
```

**Columns**:

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | INTEGER | No | **Primary Key**. Auto-increment |
| document_id | VARCHAR | No | **Foreign Key** to document_details.document_id |
| name | VARCHAR | Yes | Buyer full name |
| gender | VARCHAR | Yes | Buyer gender (Male/Female/Other) |
| aadhaar_number | VARCHAR | Yes | Aadhaar number (12 digits) |
| pan_card_number | VARCHAR | Yes | PAN card number (10 characters) |
| address | VARCHAR | Yes | Full residential address |
| pincode | VARCHAR | Yes | Address pincode |
| state | VARCHAR | Yes | Buyer state |
| phone_number | VARCHAR | Yes | Primary phone number |
| secondary_phone_number | VARCHAR | Yes | Secondary/alternate phone |
| email | VARCHAR | Yes | Email address |

**Design Notes**:
- **Identical to seller_details** except no `property_share` column
- **One-to-Many**: Multiple buyers can be associated with one document

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `document_id` (implicit from foreign key)

**Foreign Keys**:
- `document_id` → `document_details.document_id` (ON DELETE CASCADE)

**Sample Data**:
```sql
INSERT INTO buyer_details (document_id, name, gender, aadhaar_number, pan_card_number)
VALUES ('DOC_2024_001', 'Rajesh Kumar', 'Male', '1234-5678-9012', 'ABCDE1234F');
```

---

### 5. batch_sessions

**Purpose**: Track PDF upload batches and processing status

**Table Definition**:
```sql
CREATE TABLE batch_sessions (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_started_at TIMESTAMP,
    uploaded_count INTEGER DEFAULT 0,
    processed_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    batch_name VARCHAR(200),
    status VARCHAR(50) DEFAULT 'pending'
);

CREATE INDEX idx_batch_id ON batch_sessions(batch_id);
CREATE INDEX idx_created_at ON batch_sessions(created_at);
CREATE INDEX idx_processing_started_at ON batch_sessions(processing_started_at);
```

**SQLAlchemy Model**:
```python
class BatchSession(Base):
    __tablename__ = "batch_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    processing_started_at = Column(DateTime, nullable=True, index=True)
    uploaded_count = Column(Integer, default=0)
    processed_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    batch_name = Column(String(200), nullable=True)
    status = Column(String(50), default='pending')
```

**Columns**:

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | INTEGER | No | AUTO | **Primary Key**. Auto-increment |
| batch_id | VARCHAR(100) | No | - | **Unique**. Batch identifier (format: BATCH_YYYYMMDD_HHMMSS_UUID) |
| created_at | TIMESTAMP | No | CURRENT_TIMESTAMP | Upload timestamp |
| processing_started_at | TIMESTAMP | Yes | NULL | Processing start timestamp |
| uploaded_count | INTEGER | No | 0 | Number of PDFs uploaded |
| processed_count | INTEGER | No | 0 | Number of PDFs processed (reserved for future use) |
| failed_count | INTEGER | No | 0 | Number of failed PDFs (reserved for future use) |
| batch_name | VARCHAR(200) | Yes | NULL | First document name (user-friendly identifier) |
| status | VARCHAR(50) | No | 'pending' | Batch status (pending/processing/completed) |

**Status Values**:
- `pending`: Uploaded but not started processing
- `processing`: Currently being processed
- `completed`: Processing finished

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE INDEX on `batch_id`
- INDEX on `created_at` (for sorting by upload time)
- INDEX on `processing_started_at` (for sorting by processing time)

**Sample Data**:
```sql
INSERT INTO batch_sessions (batch_id, uploaded_count, batch_name, status)
VALUES ('BATCH_20241223_130000_a1b2c3d4', 15, 'Sale_Deed_2024_001', 'pending');
```

---

### 6. user_info

**Purpose**: Track user information for uploaded file batches

**Table Definition**:
```sql
CREATE TABLE user_info (
    id SERIAL PRIMARY KEY,
    user_name VARCHAR(200) NOT NULL,
    number_of_files INTEGER NOT NULL,
    file_region VARCHAR(200) NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    batch_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_batch_id ON user_info(batch_id);
```

**SQLAlchemy Model**:
```python
class UserInfo(Base):
    __tablename__ = "user_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(200), nullable=False)
    number_of_files = Column(Integer, nullable=False)
    file_region = Column(String(200), nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    batch_id = Column(String(100), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

**Columns**:

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | INTEGER | No | AUTO | **Primary Key**. Auto-increment |
| user_name | VARCHAR(200) | No | - | User's name |
| number_of_files | INTEGER | No | - | Number of files to upload |
| file_region | VARCHAR(200) | No | - | Region/location of files (e.g., Hebbal, Goa) |
| date | TIMESTAMP | No | CURRENT_TIMESTAMP | Entry creation date |
| batch_id | VARCHAR(100) | Yes | NULL | Linked batch ID (updated after upload) |
| created_at | TIMESTAMP | No | CURRENT_TIMESTAMP | Record creation timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `batch_id` (for linking to batch_sessions)

**Sample Data**:
```sql
INSERT INTO user_info (user_name, number_of_files, file_region, batch_id)
VALUES ('John Doe', 10, 'Bangalore', 'BATCH_20241223_130000_a1b2c3d4');
```

---

### 7. user_tickets

**Purpose**: Support ticket system for error reporting and issue tracking

**Table Definition**:
```sql
CREATE TABLE user_tickets (
    id SERIAL PRIMARY KEY,
    user_name VARCHAR(200) NOT NULL,
    batch_id VARCHAR(100),
    error_type VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

CREATE INDEX idx_ticket_batch_id ON user_tickets(batch_id);
```

**SQLAlchemy Model**:
```python
class UserTicket(Base):
    __tablename__ = "user_tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(200), nullable=False)
    batch_id = Column(String(100), nullable=True, index=True)
    error_type = Column(String(200), nullable=False)
    description = Column(String, nullable=False)
    status = Column(String(50), default='open')
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
```

**Columns**:

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | INTEGER | No | AUTO | **Primary Key**. Auto-increment |
| user_name | VARCHAR(200) | No | - | User reporting the issue |
| batch_id | VARCHAR(100) | Yes | NULL | Related batch ID (if applicable) |
| error_type | VARCHAR(200) | No | - | Type of error (OCR Failure, LLM Timeout, etc.) |
| description | TEXT | No | - | Detailed error description |
| status | VARCHAR(50) | No | 'open' | Ticket status (open/in_progress/resolved/closed) |
| created_at | TIMESTAMP | No | CURRENT_TIMESTAMP | Ticket creation time |
| resolved_at | TIMESTAMP | Yes | NULL | Resolution timestamp (set when status → resolved/closed) |

**Status Values**:
- `open`: Newly created ticket
- `in_progress`: Being investigated
- `resolved`: Issue resolved
- `closed`: Ticket closed

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `batch_id` (for filtering by batch)

**Sample Data**:
```sql
INSERT INTO user_tickets (user_name, batch_id, error_type, description, status)
VALUES ('John Doe', 'BATCH_20241223_130000_a1b2c3d4', 'OCR Failure',
    'OCR failed on 3 documents due to poor image quality', 'open');
```

---

## Relationships & Foreign Keys

### Relationship Diagram

```
batch_sessions (1) ←──────── (N) document_details
                                     ↓
                                     ├─ (1:1) property_details
                                     ├─ (1:N) buyer_details
                                     └─ (1:N) seller_details

user_info (N) ──────→ (1) batch_sessions (via batch_id)
user_tickets (N) ────→ (1) batch_sessions (via batch_id)
```

### Foreign Key Constraints

| Table | Column | References | On Delete |
|-------|--------|------------|-----------|
| document_details | batch_id | batch_sessions.batch_id | SET NULL |
| property_details | document_id | document_details.document_id | CASCADE |
| buyer_details | document_id | document_details.document_id | CASCADE |
| seller_details | document_id | document_details.document_id | CASCADE |

**Cascade Behavior**:
- **CASCADE**: When a document is deleted, all related property/buyer/seller records are automatically deleted
- **SET NULL**: When a batch is deleted, document batch_ids are set to NULL (documents remain)

---

## Indexes

### Primary Indexes

| Table | Index Name | Columns | Type |
|-------|-----------|---------|------|
| document_details | PK_document_details | document_id | PRIMARY KEY |
| property_details | PK_property_details | id | PRIMARY KEY |
| buyer_details | PK_buyer_details | id | PRIMARY KEY |
| seller_details | PK_seller_details | id | PRIMARY KEY |
| batch_sessions | PK_batch_sessions | id | PRIMARY KEY |
| user_info | PK_user_info | id | PRIMARY KEY |
| user_tickets | PK_user_tickets | id | PRIMARY KEY |

### Secondary Indexes

| Table | Index Name | Columns | Purpose |
|-------|-----------|---------|---------|
| document_details | idx_document_batch_id | batch_id | Fast batch filtering |
| property_details | idx_property_document_id | document_id | UNIQUE constraint + fast lookups |
| batch_sessions | idx_batch_id | batch_id | UNIQUE constraint + fast lookups |
| batch_sessions | idx_created_at | created_at | Sorting by upload time |
| batch_sessions | idx_processing_started_at | processing_started_at | Sorting by processing time |
| user_info | idx_user_batch_id | batch_id | Linking to batches |
| user_tickets | idx_ticket_batch_id | batch_id | Filtering tickets by batch |

---

## Data Types & Constraints

### Data Type Choices

| Type | Usage | Rationale |
|------|-------|-----------|
| VARCHAR | Names, addresses, IDs | Variable-length strings |
| VARCHAR(N) | Limited-length fields | Explicit size constraints |
| TEXT | Long descriptions | Unlimited text |
| INTEGER | Counters, IDs | Whole numbers |
| FLOAT | Areas, monetary values | Decimal numbers |
| DATE | Transaction dates | Date without time |
| TIMESTAMP | Audit timestamps | Date with time |

### Nullable vs NOT NULL

**NOT NULL Fields**:
- Primary keys (all `id` columns)
- Foreign keys (document_id in property/buyer/seller tables)
- Batch identifiers (batch_id in batch_sessions)
- User-provided required fields (user_name, error_type, etc.)

**NULL Allowed**:
- All extracted document fields (LLM may not extract everything)
- Optional timestamps (processing_started_at, resolved_at)
- Optional foreign keys (batch_id in document_details)

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      batch_sessions                              │
├─────────────────────────────────────────────────────────────────┤
│ PK  id (INTEGER)                                                 │
│ UNQ batch_id (VARCHAR(100))                                      │
│     created_at (TIMESTAMP)                                       │
│     processing_started_at (TIMESTAMP)                            │
│     uploaded_count (INTEGER)                                     │
│     batch_name (VARCHAR(200))                                    │
│     status (VARCHAR(50))                                         │
└──────────────────────┬──────────────────────────────────────────┘
                       │ 1
                       │
                       │ N
┌──────────────────────▼──────────────────────────────────────────┐
│                   document_details                               │
├─────────────────────────────────────────────────────────────────┤
│ PK  document_id (VARCHAR)                                        │
│ FK  batch_id (VARCHAR(100)) → batch_sessions.batch_id           │
│     transaction_date (DATE)                                      │
│     registration_office (VARCHAR)                                │
│     created_at (TIMESTAMP)                                       │
│     updated_at (TIMESTAMP)                                       │
└──────────────┬──────────────┬──────────────┬────────────────────┘
               │ 1            │ 1            │ 1
               │              │              │
               │ 1            │ N            │ N
┌──────────────▼────────┐    │              │
│  property_details     │    │              │
├───────────────────────┤    │              │
│ PK  id (INTEGER)      │    │              │
│ FK  document_id (UNQ) │    │              │
│     schedule_b_area   │    │              │
│     sale_consideration│    │              │
│     registration_fee  │    │              │
│     ... (11 columns)  │    │              │
└───────────────────────┘    │              │
                             │              │
               ┌─────────────▼─────────┐    │
               │   buyer_details       │    │
               ├───────────────────────┤    │
               │ PK  id (INTEGER)      │    │
               │ FK  document_id       │    │
               │     name              │    │
               │     aadhaar_number    │    │
               │     ... (10 columns)  │    │
               └───────────────────────┘    │
                                            │
                              ┌─────────────▼─────────┐
                              │   seller_details      │
                              ├───────────────────────┤
                              │ PK  id (INTEGER)      │
                              │ FK  document_id       │
                              │     name              │
                              │     property_share    │
                              │     ... (11 columns)  │
                              └───────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                       user_info                                  │
├─────────────────────────────────────────────────────────────────┤
│ PK  id (INTEGER)                                                 │
│     user_name (VARCHAR(200))                                     │
│     number_of_files (INTEGER)                                    │
│     file_region (VARCHAR(200))                                   │
│ FK  batch_id (VARCHAR(100)) → batch_sessions.batch_id           │
│     created_at (TIMESTAMP)                                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      user_tickets                                │
├─────────────────────────────────────────────────────────────────┤
│ PK  id (INTEGER)                                                 │
│     user_name (VARCHAR(200))                                     │
│ FK  batch_id (VARCHAR(100)) → batch_sessions.batch_id           │
│     error_type (VARCHAR(200))                                    │
│     description (TEXT)                                           │
│     status (VARCHAR(50))                                         │
│     created_at (TIMESTAMP)                                       │
│     resolved_at (TIMESTAMP)                                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Migration Strategy

### Alembic Configuration

**Migration Directory**: `backend/migrations/`

**Alembic Commands**:
```bash
# Initialize Alembic (first time only)
alembic init migrations

# Create a new migration
alembic revision --autogenerate -m "Add user_tickets table"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history
```

### Manual SQL Migrations

Located in `backend/app/migrations/`:
1. `add_batch_tracking.sql` - Added batch_sessions table
2. `add_processing_started_at.sql` - Added processing_started_at column
3. `add_user_info_and_tickets.sql` - Added user_info and user_tickets tables

---

## Performance Optimization

### Query Optimization

**Use Eager Loading for Relationships**:
```python
from sqlalchemy.orm import joinedload

documents = db.query(DocumentDetail).options(
    joinedload(DocumentDetail.property_details),
    joinedload(DocumentDetail.buyers),
    joinedload(DocumentDetail.sellers)
).all()
```

**Pagination for Large Result Sets**:
```python
documents = db.query(DocumentDetail).offset(skip).limit(limit).all()
```

**Filtering with Indexes**:
```python
# Uses idx_document_batch_id
documents = db.query(DocumentDetail).filter(
    DocumentDetail.batch_id.in_(batch_list)
).all()
```

### Index Usage

**Check Index Usage** (PostgreSQL):
```sql
EXPLAIN ANALYZE SELECT * FROM document_details WHERE batch_id = 'BATCH_20241223_130000_a1b2c3d4';
```

**Monitor Index Health**:
```sql
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

---

## Backup & Recovery

### Backup Strategy

**Full Backup** (Daily):
```bash
pg_dump -U postgres -h localhost sale_deed_db > backup_$(date +%Y%m%d).sql
```

**Schema-Only Backup**:
```bash
pg_dump -U postgres -h localhost --schema-only sale_deed_db > schema.sql
```

**Data-Only Backup**:
```bash
pg_dump -U postgres -h localhost --data-only sale_deed_db > data.sql
```

### Recovery

**Restore Full Backup**:
```bash
psql -U postgres -h localhost sale_deed_db < backup_20241223.sql
```

**Restore Specific Table**:
```bash
pg_restore -U postgres -h localhost -d sale_deed_db -t document_details backup.dump
```

---

## Database Statistics

**Schema Version**: 1.0
**Total Tables**: 7
**Total Columns**: 78
**Total Indexes**: 15 (7 primary + 8 secondary)
**Foreign Keys**: 4
**Unique Constraints**: 2

---

## Changelog

### Version 1.0 (December 2024)
- Initial database schema
- 7 core tables with relationships
- Batch tracking system
- User management tables
- Support ticket system
- Optimized indexes for fast queries

---

**Document Version**: 1.0
**Last Updated**: December 23, 2024
