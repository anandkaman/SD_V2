# SaleDeed Processor v1.0

A sophisticated desktop application for processing Indian property sale deed documents using AI/ML technologies. Extracts structured data from PDF documents and provides an Excel-like interface for viewing and exporting results.

## Overview

SaleDeed Processor combines advanced OCR, Large Language Models (LLMs), and computer vision to automatically extract critical information from property sale deed PDFs. The system features a modern React-Electron desktop interface with a powerful FastAPI backend.

## Key Features

### Document Processing
- **Dual Processing Modes**:
  - Pipeline Mode (V2): Advanced 2-stage architecture with separate OCR and LLM workers
  - Legacy Mode (V1): Simple batch processor with worker pool
- **Multi-page PDF support** with configurable parallel processing
- **Intelligent OCR**:
  - Tesseract OCR with Kannada and English support
  - PyMuPDF embedded OCR alternative
  - Poppler-based PDF to image conversion at 300 DPI
- **Advanced LLM Integration**:
  - Primary: Google Gemini 2.5 Flash Lite
  - Fallback support: Ollama, llama.cpp, vLLM, Groq
  - Automatic failover between backends
- **Computer Vision**: YOLO-based table detection and registration fee extraction

### Data Extraction
Extracts 30+ fields including:
- **Document Details**: ID, transaction date, registration office
- **Property Information**: Land area, address, pincode, state, sale consideration, stamp duty, registration fee, guidance value
- **Buyer Details**: Name, gender, Aadhaar, PAN, complete address, contact information
- **Seller Details**: Same as buyers plus property share percentage

### User Interface
- **Control Panel**:
  - Drag-and-drop PDF upload
  - Real-time processing statistics
  - Start/Stop controls with configurable worker counts
  - Progress monitoring (processed/failed counts, percentages)
  - Failed PDF reprocessing and download
  - OCR mode toggle (embedded vs Tesseract)
- **Data View**:
  - Excel-like table with 30 columns
  - Sticky headers and first column
  - Real-time search across all fields
  - Client and server-side Excel export
  - Batch filtering and date range selection
- **System Monitoring**:
  - Real-time health checks
  - CUDA, Tesseract, Ollama, YOLO status indicators
  - Folder statistics display
  - Light/Dark theme toggle

### Batch Management
- Unique batch ID tracking for upload sessions
- User information capture (name, file count, region)
- Support ticket system for error reporting
- Batch-level statistics and filtering

## Technology Stack

### Frontend
- **React 18.2.0** - Modern UI framework
- **Electron 28.0.0** - Cross-platform desktop application
- **React Router 6.20.0** - Client-side routing
- **Axios 1.6.2** - HTTP client
- **xlsx 0.18.5** - Client-side Excel export
- **Lucide React** - Icon library

### Backend
- **FastAPI 0.109.0** - Async Python web framework
- **Uvicorn 0.27.0** - ASGI server
- **PostgreSQL 13+** - Primary database
- **SQLAlchemy 2.0.25** - ORM with async support
- **Alembic 1.13.1** - Database migrations

### AI/ML & Document Processing
- **Tesseract 4.1+** - OCR engine
- **Poppler 25.07.0** - PDF rendering
- **pdfplumber 0.10.3** - Structured text extraction
- **PyMuPDF (fitz)** - Alternative OCR
- **YOLO (ONNX Runtime)** - Table detection (table1.19.1.onnx)
- **OpenCV 4.9.0** - Image processing
- **Google Gemini API** - Primary LLM
- **Ollama** - Local LLM serving
- **Groq API** - Cloud LLM fallback

### Data Processing
- **Pandas 2.1.4** - Data manipulation
- **NumPy 1.26.3** - Numerical operations
- **openpyxl** - Server-side Excel generation

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 Electron Desktop App                     │
│  ┌──────────────┐         ┌─────────────────────────┐  │
│  │ Control Panel│◄────────┤   React Frontend        │  │
│  │  Data View   │         │   (Port 3000)           │  │
│  └──────────────┘         └─────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼ (HTTP/REST API)
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend (Port 8000)                 │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐ │
│  │ API Routes  │  │  Processors  │  │   Services     │ │
│  │ (30+ eps)   │─▶│  (Pipeline)  │─▶│ OCR/LLM/Vision │ │
│  └─────────────┘  └──────────────┘  └────────────────┘ │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│          PostgreSQL Database (Port 5432)                 │
│  Documents │ Properties │ Buyers/Sellers │ Batches      │
└─────────────────────────────────────────────────────────┘

Processing Pipeline (V2):
PDF → [OCR Workers] → Text Queue → [LLM Workers] → JSON → Database
                                  ↓
                          [Vision Worker] → Fee Images → Database
```

## Installation

### Prerequisites
- **Python 3.11+** with pip
- **Node.js 18+** with npm
- **PostgreSQL 13+**
- **Tesseract OCR 4.1+** (with eng+kan language data)
- **Poppler 25.07.0** (for pdf2image)
- **CUDA 11.8+** (optional, for GPU acceleration)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd sale-deed-processor/sale_deed_processor/backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables (create `.env` file):
```env
DATABASE_URL=postgresql://postgres:admin@localhost:5432/sale_deed_db
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

4. Initialize the database:
```bash
# Create database
createdb sale_deed_db

# Run migrations
alembic upgrade head
```

5. Download the YOLO model:
   - Place `table1.19.1.onnx` in `sale_deed_processor/models/`

6. Start the backend server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd fronted
```

2. Install Node dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run electron-dev
```

### Quick Start (Windows)

Use the provided batch scripts:
```bash
# From the fronted directory
setup.bat         # First-time setup
start-dev.bat     # Start development mode
```

## Usage

### Processing PDFs

1. **Upload PDFs**:
   - Launch the application
   - Navigate to Control Panel
   - Click "Choose Files" or drag-and-drop PDFs
   - Click "Upload Files"

2. **Start Processing**:
   - Configure worker counts (OCR: 1-2, LLM: 4-8 recommended)
   - Click "Start Processing"
   - Monitor real-time statistics

3. **View Results**:
   - Navigate to Data View
   - Search, filter, and browse extracted data
   - Export to Excel (client or server-side)

4. **Handle Failures**:
   - Review failed PDFs in statistics
   - Click "Rerun Failed PDFs" to retry
   - Download failed PDFs for manual review

### Configuration

Key settings in `backend/app/config.py`:

```python
# OCR Settings
TESSERACT_LANG = "eng+kan"
POPPLER_DPI = 300
TARGET_WIDTH = 2000

# Pipeline Settings
MAX_OCR_WORKERS = 2
MAX_LLM_WORKERS = 8
STAGE2_QUEUE_SIZE = 1

# LLM Backend
LLM_BACKEND = "gemini"  # or "ollama", "groq", "llama_cpp", "vllm"
GEMINI_MODEL = "gemini-2.5-flash-lite"
TEMPERATURE = 0.6
MAX_TOKENS = 16384
```

## API Endpoints

### Upload & Processing
- `POST /api/upload` - Upload PDFs with batch tracking
- `POST /api/process/start` - Start processing
- `POST /api/process/stop` - Stop processing
- `GET /api/process/stats` - Real-time statistics
- `POST /api/process/rerun-failed` - Retry failed PDFs
- `GET /api/process/download-failed` - Download failed PDFs as ZIP

### Data Retrieval
- `GET /api/documents` - Get all documents (paginated)
- `GET /api/documents/{document_id}` - Get specific document
- `GET /api/export/excel` - Export to Excel

### System Information
- `GET /health` - Health check
- `GET /api/system/info` - System status
- `GET /api/system/config` - Pipeline configuration
- `GET /api/system/folders` - Folder statistics

### Batch Management
- `GET /api/batches` - Get batch sessions
- `POST /api/user-info` - Create user info
- `POST /api/tickets` - Create support ticket

## Database Schema

### Core Tables
- **document_details** - Main document information
- **property_details** - Property-specific data (1-to-1)
- **buyer_details** - Buyer information (1-to-many)
- **seller_details** - Seller information (1-to-many)
- **batch_sessions** - Upload batch tracking
- **user_info** - User metadata
- **user_tickets** - Support ticket system

## Building for Production

### Create Electron Installer

```bash
cd fronted
npm run build      # Build React app
npm run dist       # Create Windows installer
```

Output: `dist/SaleDeed Processor Setup 1.0.0.exe` (~100 MB)

## Performance Optimization

### Memory Management
- OCR workers limited to 2 (each uses ~500MB-1GB)
- Image resizing to 2000px width for Indic script optimization
- Bounded queue sizes to prevent memory overflow
- Automatic cleanup of processed images

### Processing Speed
- Pipeline mode: 2-5x faster than legacy mode
- Parallel OCR and LLM stages
- Configurable worker pools (scale based on CPU/GPU)
- Async I/O throughout the stack

### Recommended Settings
- **Desktop (8GB RAM)**: OCR=1, LLM=4
- **Workstation (16GB RAM)**: OCR=2, LLM=6
- **Server (32GB+ RAM)**: OCR=2, LLM=8

## Troubleshooting

### Common Issues

**OCR Failures**:
- Verify Tesseract installation: `tesseract --version`
- Check language data: `tesseract --list-langs` (should include eng, kan)
- Ensure Poppler is in PATH: `pdftoppm -v`

**LLM Errors**:
- Check API keys in `.env` file
- For Ollama: Ensure service is running (`ollama serve`)
- Verify network connectivity for cloud APIs

**Database Connection**:
- Confirm PostgreSQL is running: `pg_isready`
- Check DATABASE_URL in `.env`
- Run migrations: `alembic upgrade head`

**CUDA Not Detected**:
- Install NVIDIA drivers and CUDA toolkit 11.8+
- Verify: `nvidia-smi`
- Falls back to CPU automatically

## Project Structure

```
sale-deed-processor/
├── sale_deed_processor/          # Backend
│   ├── backend/
│   │   ├── app/
│   │   │   ├── api/              # REST endpoints
│   │   │   ├── services/         # Business logic
│   │   │   ├── workers/          # Processing pipeline
│   │   │   ├── utils/            # Helpers
│   │   │   ├── models.py         # Database models
│   │   │   ├── schemas.py        # Pydantic schemas
│   │   │   ├── config.py         # Configuration
│   │   │   └── main.py           # FastAPI app
│   │   ├── requirements.txt
│   │   └── migrations/           # Alembic
│   ├── models/                   # YOLO model
│   └── data/                     # Processing folders
│
└── fronted/                      # Frontend
    ├── src/
    │   ├── components/           # React components
    │   ├── pages/                # Main pages
    │   ├── services/             # API client
    │   ├── context/              # Theme context
    │   └── styles/               # CSS
    ├── electron/
    │   └── main.js               # Electron main process
    ├── public/
    └── package.json
```

## Contributing

### Development Workflow
1. Create feature branch from `main`
2. Make changes with descriptive commits
3. Test thoroughly (OCR, LLM, vision pipeline)
4. Submit pull request with documentation updates

### Code Style
- Python: PEP 8 (use `black` formatter)
- JavaScript: ESLint + Prettier
- Commit messages: Conventional Commits format

## License

Proprietary - All rights reserved

## Support

For issues, bug reports, or feature requests:
- Create a support ticket through the in-app system
- Contact: [Your contact information]

## Acknowledgments

- **Tesseract OCR** - Open-source OCR engine
- **Google Gemini** - LLM API
- **YOLO** - Object detection framework
- **FastAPI** - Modern Python web framework
- **React & Electron** - Desktop application framework

## Roadmap (v2.0)

Planned features:
- Multi-language support (Tamil, Telugu, Hindi)
- Bulk export with custom templates
- Advanced analytics dashboard
- Cloud deployment option
- RESTful webhook notifications
- Mobile app companion

---

**Version**: 1.0.0
**Last Updated**: December 2024
**Minimum Requirements**: Python 3.11+, Node.js 18+, PostgreSQL 13+, 8GB RAM
