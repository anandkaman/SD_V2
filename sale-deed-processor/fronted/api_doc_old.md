# Sale Deed Processor - Backend

AI-powered document processing system for extracting structured data from Indian property sale deed PDFs.

## Features

- **Multi-stage Processing Pipeline**
  - PDF text extraction with pdfplumber
  - OCR with Tesseract (Kannada + English)
  - Table detection with YOLO
  - Structured data extraction with Qwen LLM
  - Vision-based fee extraction with Qwen Vision

- **Multi-threaded Batch Processing**
  - Configurable worker threads
  - Parallel PDF processing
  - Real-time progress tracking

- **Comprehensive Data Extraction**
  - Multiple buyers and sellers per document
  - Property details with validation
  - Document metadata
  - Automatic guidance value calculation

## Prerequisites

1. **Python 3.10+**
2. **PostgreSQL** (or any SQLAlchemy-supported database)
3. **Tesseract OCR 5.5.0+** with Kannada language support
4. **Poppler** (for PDF to image conversion)
5. **Ollama** with models:
   - `qwen2.5:3b-instruct`
   - `qwen3-vl:4b`

## Installation

### 1. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-kan poppler-utils
```

**Windows:**
- Install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
- Install Poppler from: https://github.com/oschwartz10612/poppler-windows

**MacOS:**
```bash
brew install tesseract tesseract-lang poppler
```

### 2. Install Ollama and Models
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull required models
ollama pull qwen2.5:3b-instruct
ollama pull qwen3-vl:4b
```

### 3. Setup Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env
```

Update these key settings:
- `DATABASE_URL`: Your PostgreSQL connection string
- `POPPLER_PATH`: Path to Poppler binaries (Windows only)

### 5. Place YOLO Model
```bash
# Create models directory
mkdir -p ../models

# Place your table1.19.1.onnx file in the models directory
cp /path/to/table1.19.1.onnx ../models/
```

### 6. Initialize Database
```bash
python init_db.py
```

## Running the API

### Development Mode
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

API will be available at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

## Testing

### Test Single PDF
```bash
python test_single_pdf.py data/newly_uploaded/sample.pdf
```

### Test API Endpoints
```bash
# Check system health
curl http://localhost:8000/health

# Get system info
curl http://localhost:8000/api/system/info

# Upload PDF
curl -X POST http://localhost:8000/api/upload \
  -F "files=@sample.pdf"
```

## Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── api/
│   │   └── routes.py        # API endpoints
│   ├── services/
│   │   ├── pdf_processor.py           # Main orchestrator
│   │   ├── registration_fee_extractor.py  # pdfplumber extraction
│   │   ├── ocr_service.py             # Tesseract OCR
│   │   ├── yolo_detector.py           # YOLO table detection
│   │   ├── llm_service.py             # LLM integration
│   │   ├── vision_service.py          # Vision model integration
│   │   └── validation_service.py      # Data validation
│   ├── utils/
│   │   ├── file_handler.py  # File operations
│   │   └── prompts.py       # LLM prompts
│   └── workers/
│       ├── batch_processor.py         # PDF batch processing
│       └── vision_batch_processor.py  # Vision batch processing
├── init_db.py               # Database initialization
├── test_single_pdf.py       # Testing script
├── requirements.txt         # Python dependencies
└── .env                     # Environment variables
```

## API Endpoints

### Upload
- `POST /api/upload` - Upload PDF files

### Processing Control
- `POST /api/process/start` - Start PDF batch processing
- `POST /api/process/stop` - Stop PDF batch processing
- `GET /api/process/stats` - Get processing statistics

### Vision Processing
- `POST /api/vision/start` - Start vision batch processing
- `POST /api/vision/stop` - Stop vision batch processing
- `GET /api/vision/stats` - Get vision statistics

### Data Retrieval
- `GET /api/documents` - Get all documents (paginated)
- `GET /api/documents/{document_id}` - Get specific document
- `GET /api/export/excel` - Export data to Excel

### System
- `GET /api/system/info` - System health and capabilities
- `GET /api/system/folders` - Folder statistics

## Configuration

### Adjusting Worker Count

Edit `MAX_WORKERS` in `.env` or `config.py`:
```python
MAX_WORKERS=2  # Number of parallel PDF processing threads
```

### Adjusting OCR Settings

Edit Tesseract config in `.env`:
```bash
TESSERACT_LANG=eng+kan
TESSERACT_OEM=1  # LSTM neural nets mode
TESSERACT_PSM=6  # Assume uniform block of text
```

### Adjusting YOLO Confidence

Edit in `.env`:
```bash
YOLO_CONF_THRESHOLD=0.65
```

## Troubleshooting

### Ollama Connection Failed
```bash
# Check if Ollama is running
ollama list

# Start Ollama service
ollama serve
```

### Tesseract Not Found
```bash
# Verify Tesseract installation
tesseract --version

# Check language packs
tesseract --list-langs
```

### Database Connection Error
- Verify PostgreSQL is running
- Check DATABASE_URL in .env
- Ensure database exists

### Slow Processing
- Increase MAX_WORKERS for more parallelism
- Use SSD for data directories
- Ensure CUDA is available for faster processing

## Performance Notes

- **OCR Speed**: ~2-3 seconds per page at 300 DPI
- **LLM Extraction**: ~5-10 seconds per document
- **Batch Processing**: ~15-20 seconds per PDF (2 workers)
- **Vision Model**: ~3-5 seconds per table image

## License

Proprietary - Internal Use Only
and
#!/bin/bash
# backend/setup.sh

echo "================================"
echo "Sale Deed Processor - Setup"
echo "================================"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env from template
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Please edit .env with your configuration"
fi

# Create directories
echo "Creating data directories..."
python init_db.py

echo ""
echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Edit .env with your database credentials"
echo "2. Place YOLO model (table1.19.1.onnx) in models/ directory"
echo "3. Ensure Ollama is running: ollama serve"
echo "4. Start API: uvicorn app.main:app --reload"
echo ""
help me with use my app for first time on windows
.