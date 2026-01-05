# Sale Deed AI - Document Processing System

**Income Tax Department - Automated Sale Deed Processing Platform**

A comprehensive AI-powered system for processing sale deed documents, extracting structured data, and managing document workflows with advanced OCR and LLM capabilities.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Recent Enhancements](#recent-enhancements)
- [Database Schema](#database-schema)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## 🎯 Overview

Sale Deed AI is an enterprise-grade document processing system designed for the Income Tax Department to automate the extraction and management of sale deed information. The system combines OCR technology, computer vision (YOLO), and Large Language Models (LLM) to extract structured data from PDF documents with high accuracy.

### Key Capabilities

- **Batch Processing**: Process thousands of PDFs concurrently with configurable worker pools
- **Intelligent OCR**: Dual-mode OCR (PyMuPDF embedded + Tesseract) with automatic fallback
- **Vision-Based Extraction**: YOLO + Qwen2-VL for registration fee table detection
- **LLM Data Parsing**: Structured data extraction with validation and cleaning
- **Batch Management**: Track processing sessions with detailed statistics
- **Failed Document Recovery**: Batch-level retry with detailed failure tracking
- **CSV Export**: 42-column format export with comprehensive data mapping
- **User Management**: Track user sessions, tickets, and processing history

---

## ✨ Features

### Document Processing
- ✅ Multi-file PDF upload with drag-and-drop
- ✅ Dual OCR modes (embedded PyMuPDF / Tesseract)
- ✅ Configurable OCR and LLM worker pools (1-20 workers)
- ✅ Pipeline architecture (separate OCR and LLM stages)
- ✅ Real-time processing statistics
- ✅ Automatic batch session tracking

### Data Extraction
- ✅ **Buyer Details**: Name, gender, father's name, DOB, Aadhaar, PAN, address, contact
- ✅ **Seller Details**: Name, gender, father's name, DOB, Aadhaar, PAN, address, contact, property share
- ✅ **Confirming Party Details**: Complete party information with father's name and DOB
- ✅ **Property Details**: Areas, addresses, sale consideration, fees, guidance value
- ✅ **Registration Fee**: Multi-method extraction with ratio validation
- ✅ **Document Metadata**: Transaction date, registration office, batch tracking

### Advanced Features
- ✅ **Vision Processing**: YOLO-based table detection for registration fees
- ✅ **Batch-Based Retry**: Retry failed documents by specific batch
- ✅ **Failed Document Tracking**: View failed files grouped by batch
- ✅ **CSV Export**: 42-column format with sellers (S), buyers (B), confirming parties (C)
- ✅ **Data Validation**: Comprehensive cleaning and validation service
- ✅ **Ticket System**: User support ticket management
- ✅ **Tour Guide**: Interactive onboarding for new users

---

## 🛠 Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.8+)
- **Database**: SQLite with SQLAlchemy ORM
- **OCR**: PyMuPDF (embedded), Tesseract OCR, Poppler
- **Computer Vision**: YOLO (Ultralytics), Qwen2-VL
- **LLM**: Ollama (local) / Google Gemini API
- **Processing**: Multiprocessing, ThreadPoolExecutor
- **Data Export**: Pandas, OpenPyXL, CSV

### Frontend
- **Framework**: React 18
- **Routing**: React Router DOM
- **Icons**: Lucide React
- **Styling**: Custom CSS with responsive design
- **Tour**: React Joyride for guided tours

### Infrastructure
- **GPU Support**: CUDA for YOLO and vision models
- **File Management**: Organized folder structure for processing stages
- **Logging**: Comprehensive logging with rotation

---

## 📁 Project Structure

```
sale-deed-processor/
├── fronted/                          # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/              # Reusable components
│   │   ├── config/                  # Tour steps, configurations
│   │   ├── pages/
│   │   │   ├── ControlPanel.js      # Main processing interface
│   │   │   └── DataView.js          # Data viewing and export
│   │   ├── services/
│   │   │   └── api.js               # API client
│   │   └── styles/                  # CSS stylesheets
│   └── package.json
│
├── sale_deed_processor/             # Python backend
│   ├── backend/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   │   └── routes.py        # API endpoints
│   │   │   ├── models.py            # Database models
│   │   │   ├── schemas.py           # Pydantic schemas
│   │   │   ├── database.py          # Database configuration
│   │   │   ├── config.py            # Application settings
│   │   │   ├── main.py              # FastAPI application
│   │   │   ├── services/
│   │   │   │   ├── ocr_service.py
│   │   │   │   ├── pdf_processor_v2.py
│   │   │   │   ├── registration_fee_extractor.py
│   │   │   │   ├── validation_service.py
│   │   │   │   ├── csv_export_service.py
│   │   │   │   ├── gemini_vision_service.py
│   │   │   │   └── transliteration.py
│   │   │   └── utils/
│   │   │       ├── prompts.py       # LLM prompts
│   │   │       └── file_handler.py
│   │   └── data/
│   │       ├── newly_uploaded/      # Upload destination
│   │       ├── processed/           # Successfully processed
│   │       ├── failed/              # Failed documents
│   │       └── left_over_reg_fee/   # Vision processing queue
│   └── requirements.txt
│
├── poppler/                         # Poppler binaries for PDF processing
├── start_app.bat                    # Windows startup script
└── README.md                        # This file
```

---

## 🚀 Installation

### Prerequisites

1. **Python 3.8+**
2. **Node.js 16+** and npm
3. **CUDA Toolkit** (optional, for GPU acceleration)
4. **Tesseract OCR** (for traditional OCR mode)
5. **Poppler** (included in project)

### Backend Setup

```bash
# Navigate to backend directory
cd sale_deed_processor/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from app.database import init_db; init_db()"

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd fronted

# Install dependencies
npm install

# Start development server
npm start
```

### Quick Start (Windows)

**Start All Services:**
```bash
# Double-click the PM2 start script
pm2-start.bat
```

**Stop All Services:**
```bash
# Double-click the PM2 stop script
pm2-stop.bat
```

This will:
1. Start the backend server on `http://localhost:8000`
2. Start the frontend Electron app
3. Manage all services with PM2 process manager

For detailed PM2 commands and troubleshooting, see [PM2_GUIDE.md](PM2_GUIDE.md)

---

## ⚙️ Configuration

### Backend Configuration (`backend/app/config.py`)

```python
# Processing Configuration
ENABLE_PIPELINE = True           # Use pipeline mode (recommended)
MAX_OCR_WORKERS = 5              # OCR worker pool size
MAX_LLM_WORKERS = 5              # LLM worker pool size
STAGE2_QUEUE_SIZE = 2            # Queue size between stages
ENABLE_OCR_MULTIPROCESSING = False  # OCR page-level multiprocessing
OCR_PAGE_WORKERS = 2             # Workers per OCR page

# OCR Configuration
USE_EMBEDDED_OCR = False         # PyMuPDF (True) vs Tesseract (False)
TESSERACT_LANG = 'eng+kan'       # OCR languages
POPPLER_DPI = 300                # PDF to image DPI

# LLM Configuration
LLM_BACKEND = 'ollama'           # 'ollama' or 'gemini'
OLLAMA_BASE_URL = 'http://localhost:11434'
GEMINI_API_KEY = 'your-api-key'  # If using Gemini

# Vision Model Configuration
YOLO_MODEL_PATH = 'path/to/yolo/model'
VISION_MODEL_URL = 'http://localhost:8001'
```

### Environment Variables

Create `.env` file in backend directory:

```env
DATABASE_URL=sqlite:///./sale_deeds.db
GEMINI_API_KEY=your_gemini_api_key_here
OLLAMA_BASE_URL=http://localhost:11434
```

---

## 📖 Usage

### 1. Upload Documents

1. Navigate to Control Panel
2. Select PDF files (drag-and-drop or click to browse)
3. Fill in user information:
   - User Name
   - Number of Files
   - File Region/Location
4. Click "Upload PDFs"

### 2. Start Processing

1. Configure worker settings:
   - OCR Workers (1-20)
   - LLM Workers (1-20)
   - Queue Size (1-10)
2. Toggle OCR mode if needed
3. Click "Start Processing"
4. Monitor real-time statistics

### 3. View Data

1. Navigate to Data View
2. Use search and filters
3. Switch between Row-wise and Batch-wise views
4. Download data as CSV

### 4. Export Data

**CSV Export (42-column format):**
1. Click "Download CSV"
2. Select export option:
   - Download All Documents
   - Download by Batch/Session
   - Download by Date Range
3. File downloads automatically

### 5. Handle Failed Documents

1. Click on "Failed Documents" stat in Control Panel
2. View failed files grouped by batch
3. Expand batch to see file list
4. Click "Retry Batch" to reprocess specific batch

---

## 🔌 API Documentation

### Processing Endpoints

#### Start Processing
```http
POST /api/process/start
Content-Type: application/json

{
  "ocr_workers": 5,
  "llm_workers": 5,
  "stage2_queue_size": 2,
  "enable_ocr_multiprocessing": false,
  "ocr_page_workers": 2
}
```

#### Stop Processing
```http
POST /api/process/stop
```

#### Get Processing Stats
```http
GET /api/process/stats
```

### Document Endpoints

#### Get All Documents
```http
GET /api/documents?skip=0&limit=100
```

#### Get Document by ID
```http
GET /api/documents/{document_id}
```

### Export Endpoints

#### Export to CSV
```http
GET /api/export/csv?download_type=all
GET /api/export/csv?batch_ids=batch1,batch2&download_type=batch
GET /api/export/csv?start_date=2024-01-01&end_date=2024-12-31&download_type=dateRange
```

### Failed Documents Endpoints

#### Get Failed Documents
```http
GET /api/process/failed-documents
```

Response:
```json
{
  "success": true,
  "total_failed_files": 10,
  "batch_count": 3,
  "batches": [
    {
      "batch_id": "batch_123",
      "batch_name": "Batch 2024-01-01",
      "total_processed": 100,
      "failed_count": 5,
      "failed_files": [
        {
          "filename": "batch_123_doc1.pdf",
          "document_id": "doc1",
          "size": 1024000,
          "modified": "2024-01-01T10:00:00"
        }
      ]
    }
  ]
}
```

#### Retry Failed Batch
```http
POST /api/process/rerun-failed-batch?batch_id=batch_123
```

### Batch Endpoints

#### Get All Batches
```http
GET /api/batches
```

---

## 🆕 Recent Enhancements

### December 2024 - Major Updates

#### 1. CSV Export with 42-Column Format ✅
- **Feature**: Export data in standardized 42-column CSV format
- **Columns**: Report serial, transaction details, property info, person details
- **Mapping**: `registration_fee` → "Stamp Value"
- **New Fields**: `father_name`, `date_of_birth` for all parties
- **Download Options**: All documents, by batch, by date range
- **Files Modified**: 
  - `backend/app/services/csv_export_service.py` (new)
  - `backend/app/api/routes.py`
  - `fronted/src/services/api.js`
  - `fronted/src/pages/DataView.js`

#### 2. Father's Name and Date of Birth Extraction ✅
- **Feature**: Extract father's name and DOB for buyers, sellers, confirming parties
- **Patterns**: S/O, D/O, W/O, Kannada equivalents (ಮಗ, ಮಗಳು, ಪತ್ನಿ)
- **Validation**: Added to ValidationService cleaning logic
- **Database**: Fields added to all party detail models
- **Files Modified**:
  - `backend/app/utils/prompts.py`
  - `backend/app/services/validation_service.py`
  - `backend/app/services/pdf_processor_v2.py`

#### 3. Confirming Party Details Support ✅
- **Feature**: Full support for confirming party information
- **Fields**: Name, gender, father_name, DOB, Aadhaar, PAN, address, contact
- **Database**: New `confirming_party_details` table
- **Validation**: Integrated into ValidationService
- **Export**: Included in CSV export with "C" relation type

#### 4. Registration Fee Extraction Improvements ✅
- **Fix**: Disabled Pattern 1 to ensure consistent validation
- **Enhancement**: Page-by-page processing for multi-page tables
- **Validation**: Ratio check (registration_fee / total_fee)
- **Robustness**: Reject ratio = 1.0 (suspicious values)
- **Minimum Numbers**: Require ≥ 3 numbers for validation

#### 5. Control Panel Enhancements ✅
- **Batch-Based Retry**: Retry failed documents by specific batch
- **Failed Document Visibility**: View failed files grouped by batch
- **Batch Status Fix**: Batches now show correct status (pending/processing/completed) ✨ NEW
- **Recent Batches Display Fix**: Fixed overflow issue causing batch items to be cut off
- **Recent Batches View More**: Toggle between 5 and all batches
- **Batch Search**: Search functionality for batch list
- **Auto-fill Number of Files**: User Info Modal automatically fills file count
- **Files Modified**:
  - `backend/app/api/routes.py` (2 new endpoints)
  - `backend/app/workers/pipeline_processor_v2.py` (batch status update)
  - `fronted/src/services/api.js`
  - `fronted/src/pages/ControlPanel.js`
  - `fronted/src/styles/ControlPanel.css`

---

## 🗄️ Database Schema

### Core Tables

#### `document_details`
- `id`: Primary key
- `document_id`: Unique document identifier
- `batch_id`: Batch session reference
- `transaction_date`: Transaction date
- `registration_office`: Registration office name
- `created_at`: Timestamp

#### `property_details`
- `id`: Primary key
- `document_id`: Foreign key
- `schedule_b_area`: Area from Schedule B
- `schedule_c_property_area`: Area from Schedule C
- `schedule_c_property_address`: Property address
- `schedule_c_property_name`: Property name
- `pincode`: Property pincode
- `state`: Property state
- `sale_consideration`: Sale amount
- `stamp_duty_fee`: Stamp duty
- `registration_fee`: Registration fee
- `guidance_value`: Guidance value
- `paid_in_cash_mode`: Cash payment details

#### `buyer_details`
- `id`: Primary key
- `document_id`: Foreign key
- `name`: Buyer name
- `gender`: Gender
- `father_name`: Father's name ✨ NEW
- `date_of_birth`: Date of birth ✨ NEW
- `aadhaar_number`: Aadhaar number
- `pan_card_number`: PAN number
- `address`: Address
- `pincode`: Pincode
- `state`: State
- `phone_number`: Phone
- `secondary_phone_number`: Secondary phone
- `email`: Email

#### `seller_details`
- Same as `buyer_details` plus:
- `property_share`: Property share percentage

#### `confirming_party_details` ✨ NEW
- Same fields as `buyer_details`

#### `batch_sessions`
- `id`: Primary key
- `batch_id`: Unique batch identifier
- `batch_name`: Batch name (first file)
- `status`: Processing status
- `created_at`: Creation timestamp
- `processing_started_at`: Processing start time

#### `user_info`
- `id`: Primary key
- `user_name`: User name
- `number_of_files`: File count
- `file_region`: Region/location
- `batch_id`: Associated batch
- `created_at`: Timestamp

#### `user_tickets`
- `id`: Primary key
- `user_name`: User name
- `batch_id`: Related batch
- `error_type`: Error category
- `description`: Issue description
- `status`: Ticket status
- `created_at`: Creation time
- `resolved_at`: Resolution time

---

## 🔧 Troubleshooting

### Common Issues

#### 1. OCR Not Working
**Problem**: No text extracted from PDFs

**Solutions**:
- Check Tesseract installation: `tesseract --version`
- Verify Poppler path in config
- Try switching OCR mode (embedded vs traditional)
- Check PDF quality and DPI settings

#### 2. LLM Not Responding
**Problem**: Structured data extraction fails

**Solutions**:
- Verify Ollama is running: `curl http://localhost:11434`
- Check model is loaded: `ollama list`
- Review LLM logs for errors
- Try switching to Gemini API

#### 3. Registration Fee Not Extracted
**Problem**: Registration fee shows as null

**Solutions**:
- Check if YOLO model is loaded
- Verify vision service is running
- Review registration fee extractor logs
- Check if table is in expected format

#### 4. Failed Documents Not Retrying
**Problem**: Batch retry doesn't work

**Solutions**:
- Check failed folder has files
- Verify batch_id in filename format
- Check file permissions
- Review API logs for errors

#### 5. CSV Export Missing Fields
**Problem**: Some columns are empty in CSV

**Solutions**:
- Verify LLM extracted the data (check logs)
- Check ValidationService didn't strip fields
- Review database for actual data
- Check CSV mapping in `csv_export_service.py`

---

## 📊 Performance Optimization

### Recommended Settings

**For High Volume (1000+ files):**
```python
MAX_OCR_WORKERS = 10
MAX_LLM_WORKERS = 10
STAGE2_QUEUE_SIZE = 5
ENABLE_OCR_MULTIPROCESSING = True
OCR_PAGE_WORKERS = 4
```

**For Accuracy (Complex Documents):**
```python
MAX_OCR_WORKERS = 3
MAX_LLM_WORKERS = 3
STAGE2_QUEUE_SIZE = 2
USE_EMBEDDED_OCR = False  # Use Tesseract
POPPLER_DPI = 400
```

**For Speed (Simple Documents):**
```python
MAX_OCR_WORKERS = 15
MAX_LLM_WORKERS = 15
STAGE2_QUEUE_SIZE = 10
USE_EMBEDDED_OCR = True  # Use PyMuPDF
```

---

## 🤝 Contributing

### Development Workflow

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Update documentation
5. Submit pull request

### Code Style

- **Python**: PEP 8
- **JavaScript**: ESLint + Prettier
- **Comments**: Clear and concise
- **Logging**: Use appropriate log levels

---

## 📝 License

Proprietary - Income Tax Department

---

## 👥 Support

For issues and support:
1. Check troubleshooting section
2. Review logs in `backend/logs/`
3. Create a ticket in the system
4. Contact development team

---

## 🎯 Roadmap

### Planned Features

- [ ] Multi-language support (Hindi, regional languages)
- [ ] Advanced analytics dashboard
- [ ] Automated quality scoring
- [ ] Integration with external systems
- [ ] Mobile app for document upload
- [ ] Real-time collaboration features

---

**Version**: 2.0.0  
**Last Updated**: December 31, 2024  
**Maintained By**: Income Tax Department Development Team
