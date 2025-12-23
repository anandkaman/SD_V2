# SaleDeed Processor - System Configuration Guide v1.0

**Purpose**: Comprehensive configuration reference for all system settings
**Last Updated**: December 2024

## Table of Contents

1. [Overview](#overview)
2. [Backend Configuration](#backend-configuration)
3. [Frontend Configuration](#frontend-configuration)
4. [Database Configuration](#database-configuration)
5. [OCR Configuration](#ocr-configuration)
6. [LLM Configuration](#llm-configuration)
7. [Processing Pipeline Configuration](#processing-pipeline-configuration)
8. [Performance Tuning](#performance-tuning)
9. [Environment Variables](#environment-variables)

---

## Overview

### Configuration Files

| File | Location | Purpose |
|------|----------|---------|
| config.py | backend/app/config.py | Backend settings |
| .env | backend/.env | Environment variables (not committed) |
| api.js | fronted/src/services/api.js | Frontend API configuration |
| package.json | fronted/package.json | Frontend dependencies & scripts |
| requirements.txt | backend/requirements.txt | Backend dependencies |

### Configuration Hierarchy

```
1. Environment Variables (.env)          ← Highest priority
2. Config Class Defaults (config.py)
3. Hard-coded Defaults
```

---

## Backend Configuration

### Main Configuration File

**File**: `backend/app/config.py`

```python
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # ============ DATABASE ============
    DATABASE_URL: str = "postgresql://postgres:admin@localhost:5432/sale_deed_db"

    # ============ API KEYS ============
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""

    # ============ LLM BACKEND ============
    LLM_BACKEND: str = "gemini"  # Options: gemini, ollama, groq, llama_cpp, vllm
    GEMINI_MODEL: str = "gemini-2.5-flash-lite"
    OLLAMA_MODEL: str = "llama2"
    GROQ_MODEL: str = "llama3-70b-8192"

    # LLM Request Settings
    TEMPERATURE: float = 0.6
    MAX_TOKENS: int = 16384
    LLM_TIMEOUT: int = 300  # seconds

    # ============ PROCESSING PIPELINE ============
    ENABLE_PIPELINE: bool = True  # Use Pipeline Mode (V2) vs Legacy Mode (V1)

    # Pipeline V2 Settings
    MAX_OCR_WORKERS: int = 2       # Stage 1: OCR workers
    MAX_LLM_WORKERS: int = 8       # Stage 2: LLM workers
    STAGE2_QUEUE_SIZE: int = 1     # Bounded queue size (1-10)

    # OCR Multiprocessing
    ENABLE_OCR_MULTIPROCESSING: bool = True  # Page-level parallelism
    OCR_PAGE_WORKERS: int = 1               # Workers per PDF page

    # Legacy V1 Settings
    MAX_WORKERS: int = 2  # Total workers for legacy mode

    # ============ OCR SETTINGS ============
    TESSERACT_LANG: str = "eng+kan"  # Languages: English + Kannada
    POPPLER_DPI: int = 300           # PDF to image DPI
    TARGET_WIDTH: int = 2000         # Resize images to this width (px)

    # OCR Mode
    USE_EMBEDDED_OCR: bool = False   # True: PyMuPDF, False: Tesseract

    # ============ YOLO MODEL ============
    YOLO_MODEL_PATH: Path = Path("models/table1.19.1.onnx")
    YOLO_CONFIDENCE_THRESHOLD: float = 0.88

    # ============ FILE PATHS ============
    DATA_DIR: Path = Path("data")
    NEWLY_UPLOADED_DIR: Path = DATA_DIR / "newly_uploaded"
    PROCESSED_DIR: Path = DATA_DIR / "processed"
    FAILED_DIR: Path = DATA_DIR / "failed"
    LEFT_OVER_REG_FEE_DIR: Path = DATA_DIR / "left_over_reg_fee"
    VISION_FAILED_DIR: Path = DATA_DIR / "vision_failed"
    MODELS_DIR: Path = Path("models")

    # ============ LOGGING ============
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

### Configuration Sections Explained

#### Database Configuration

```python
DATABASE_URL: str = "postgresql://postgres:admin@localhost:5432/sale_deed_db"
```

Format: `postgresql://user:password@host:port/database`

**Options**:
- **Local Development**: `localhost:5432`
- **Docker**: `postgres_container:5432`
- **Remote**: `your-server.com:5432`

#### API Keys

```python
GEMINI_API_KEY: str = ""
GROQ_API_KEY: str = ""
```

**Get API Keys**:
- Gemini: https://makersuite.google.com/app/apikey
- Groq: https://console.groq.com/keys

**Security**: Never commit API keys to git. Use `.env` file.

#### LLM Backend Selection

```python
LLM_BACKEND: str = "gemini"
```

**Available Backends**:
- `gemini`: Google Gemini API (cloud, fast, accurate)
- `ollama`: Local LLM server (privacy, offline)
- `groq`: Groq cloud API (very fast, limited free tier)
- `llama_cpp`: Local llama.cpp (CPU inference)
- `vllm`: High-performance local server (GPU required)

**Model Names**:
```python
GEMINI_MODEL: str = "gemini-2.5-flash-lite"  # Fast, cheap
# or
GEMINI_MODEL: str = "gemini-1.5-pro"         # More accurate, expensive

OLLAMA_MODEL: str = "llama2"       # 7B model
# or
OLLAMA_MODEL: str = "mistral"      # Alternative model

GROQ_MODEL: str = "llama3-70b-8192"  # 70B model with 8K context
```

#### LLM Request Settings

```python
TEMPERATURE: float = 0.6      # Randomness (0.0-1.0, lower = more deterministic)
MAX_TOKENS: int = 16384       # Maximum response length
LLM_TIMEOUT: int = 300        # Request timeout (seconds)
```

**Temperature Guide**:
- `0.0-0.3`: Very deterministic (recommended for data extraction)
- `0.4-0.7`: Balanced (default)
- `0.8-1.0`: Creative (not recommended for structured data)

---

## Frontend Configuration

### API Configuration

**File**: `fronted/src/services/api.js`

```javascript
const API_BASE_URL = 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000,  // 5 minutes
  headers: {
    'Content-Type': 'application/json',
  },
});
```

**Production**: Change to your deployed backend URL:
```javascript
const API_BASE_URL = 'https://your-domain.com/api';
```

### Polling Intervals

**File**: `fronted/src/pages/ControlPanel.js`

```javascript
// Processing stats polling (every 2 seconds)
useEffect(() => {
  const interval = setInterval(fetchStats, 2000);
  return () => clearInterval(interval);
}, []);
```

**File**: `fronted/src/components/Footer.js`

```javascript
// System health polling (every 10 seconds)
useEffect(() => {
  const interval = setInterval(fetchSystemInfo, 10000);
  return () => clearInterval(interval);
}, []);
```

**Adjust for slower networks**:
```javascript
const interval = setInterval(fetchStats, 5000);  // 5 seconds
```

---

## Database Configuration

### Connection Pool Settings

**File**: `backend/app/database.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=5,           # Number of connections to keep
    max_overflow=10,       # Extra connections when pool full
    pool_recycle=3600,     # Recycle connections after 1 hour
    pool_pre_ping=True,    # Test connections before use
    echo=False             # Log SQL queries (True for debugging)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

**Tuning Guidelines**:
- **Small App** (1-10 users): `pool_size=5, max_overflow=5`
- **Medium App** (10-50 users): `pool_size=10, max_overflow=20`
- **Large App** (50+ users): `pool_size=20, max_overflow=40`

### PostgreSQL Server Configuration

**File**: `postgresql.conf` (usually in `/etc/postgresql/13/main/`)

```ini
# Connection Settings
max_connections = 100          # Adjust based on pool size

# Memory Settings
shared_buffers = 256MB         # 25% of RAM (for dedicated server)
effective_cache_size = 1GB     # 50-75% of RAM
work_mem = 4MB                 # Per query operation
maintenance_work_mem = 64MB    # For VACUUM, CREATE INDEX

# Performance
random_page_cost = 1.1         # For SSD (4.0 for HDD)
effective_io_concurrency = 200 # For SSD (2 for HDD)

# Logging
log_statement = 'all'          # Log all queries (development only)
log_duration = on              # Log query duration
```

**Apply Changes**:
```bash
sudo systemctl restart postgresql
```

---

## OCR Configuration

### Tesseract Settings

```python
TESSERACT_LANG: str = "eng+kan"  # Languages to use
POPPLER_DPI: int = 300           # Image resolution
TARGET_WIDTH: int = 2000         # Resize for memory efficiency
```

**Language Support**:
- `eng`: English
- `kan`: Kannada (Indian regional language)
- `hin`: Hindi
- `tam`: Tamil
- `tel`: Telugu

**Add More Languages**:
```python
TESSERACT_LANG: str = "eng+kan+hin+tam+tel"
```

**Download Language Data**:
```bash
# macOS
brew install tesseract-lang

# Ubuntu
sudo apt install tesseract-ocr-hin tesseract-ocr-tam tesseract-ocr-tel

# Windows: Download from
# https://github.com/tesseract-ocr/tessdata
```

### DPI Settings

```python
POPPLER_DPI: int = 300
```

**DPI Guide**:
- `150`: Fast, low quality (not recommended)
- `200`: Balanced (for good quality PDFs)
- `300`: High quality (recommended, default)
- `400-600`: Very high quality (slow, large memory)

**Image Width**:
```python
TARGET_WIDTH: int = 2000  # Optimized for Indic scripts
```

Larger images = better OCR but more memory:
- `1500`: Low memory systems
- `2000`: Default (recommended)
- `3000`: High accuracy (requires 16GB+ RAM)

### OCR Mode Selection

```python
USE_EMBEDDED_OCR: bool = False
```

**Modes**:
- `False`: **Poppler + Tesseract** (slower, works with scanned PDFs)
- `True`: **PyMuPDF Embedded OCR** (faster, requires embedded text in PDF)

**When to Use Each**:
- Scanned PDFs → `False` (Tesseract)
- Digital PDFs with embedded text → `True` (PyMuPDF)

---

## LLM Configuration

### Gemini Configuration

```python
GEMINI_API_KEY: str = ""
GEMINI_MODEL: str = "gemini-2.5-flash-lite"
TEMPERATURE: float = 0.6
MAX_TOKENS: int = 16384
```

**Models**:
- `gemini-2.5-flash-lite`: Fastest, cheapest
- `gemini-1.5-flash`: Fast, good quality
- `gemini-1.5-pro`: Best quality, expensive

**Rate Limits** (free tier):
- 15 requests/minute
- 1 million tokens/day

### Ollama Configuration

```python
LLM_BACKEND: str = "ollama"
OLLAMA_MODEL: str = "llama2"
```

**Start Ollama Server**:
```bash
ollama serve  # Runs on localhost:11434
```

**Available Models**:
```bash
ollama list          # List installed models
ollama pull llama2   # Download llama2
ollama pull mistral  # Download mistral
```

**Model Recommendations**:
- `llama2:7b`: Fast, 4GB RAM
- `llama2:13b`: Better quality, 8GB RAM
- `mistral:7b`: Good balance
- `llama3:8b`: Latest, best quality

### Groq Configuration

```python
LLM_BACKEND: str = "groq"
GROQ_API_KEY: str = ""
GROQ_MODEL: str = "llama3-70b-8192"
```

**Models**:
- `llama3-70b-8192`: Best quality, 8K context
- `llama3-8b-8192`: Faster, 8K context
- `mixtral-8x7b-32768`: 32K context window

---

## Processing Pipeline Configuration

### Pipeline Mode (V2)

```python
ENABLE_PIPELINE: bool = True
MAX_OCR_WORKERS: int = 2
MAX_LLM_WORKERS: int = 8
STAGE2_QUEUE_SIZE: int = 1
ENABLE_OCR_MULTIPROCESSING: bool = True
OCR_PAGE_WORKERS: int = 1
```

**Worker Configuration**:

| System | OCR Workers | LLM Workers | Queue Size |
|--------|-------------|-------------|------------|
| Laptop (8GB) | 1 | 4 | 1 |
| Desktop (16GB) | 2 | 6 | 2 |
| Workstation (32GB) | 2 | 8 | 3 |
| Server (64GB+) | 3 | 12 | 5 |

**OCR Workers**:
- Each worker uses ~500MB-1GB RAM
- Limited by memory, not CPU
- Recommended: 1-2 workers

**LLM Workers**:
- I/O bound (waiting for API responses)
- Can run many in parallel
- Recommended: 4-8 workers

**Queue Size**:
- Controls memory usage
- Larger = more buffering, higher memory
- Recommended: 1-3

**OCR Multiprocessing**:
```python
ENABLE_OCR_MULTIPROCESSING: bool = True  # Page-level parallelism
OCR_PAGE_WORKERS: int = 1                # Workers per page
```

- `True`: Process pages in parallel (faster, more memory)
- `False`: Process pages sequentially (slower, less memory)

### Legacy Mode (V1)

```python
ENABLE_PIPELINE: bool = False
MAX_WORKERS: int = 2
```

**Not recommended** - use only for debugging or comparison.

---

## Performance Tuning

### Memory Optimization

**Reduce Memory Usage**:
```python
MAX_OCR_WORKERS: int = 1        # Single OCR worker
STAGE2_QUEUE_SIZE: int = 1      # Minimal queue
TARGET_WIDTH: int = 1500        # Smaller images
ENABLE_OCR_MULTIPROCESSING: bool = False  # Sequential pages
```

**Maximum Performance** (requires 32GB+ RAM):
```python
MAX_OCR_WORKERS: int = 3
MAX_LLM_WORKERS: int = 12
STAGE2_QUEUE_SIZE: int = 5
TARGET_WIDTH: int = 2500
ENABLE_OCR_MULTIPROCESSING: bool = True
OCR_PAGE_WORKERS: int = 2
```

### CPU Optimization

**High CPU Usage** (8+ cores):
```python
ENABLE_OCR_MULTIPROCESSING: bool = True
OCR_PAGE_WORKERS: int = 4       # Use more cores
```

**Low CPU** (2-4 cores):
```python
ENABLE_OCR_MULTIPROCESSING: bool = False
OCR_PAGE_WORKERS: int = 1
```

### Network Optimization

**Slow Network**:
```python
LLM_TIMEOUT: int = 600          # 10 minutes
MAX_LLM_WORKERS: int = 4        # Fewer concurrent requests
```

**Fast Network**:
```python
LLM_TIMEOUT: int = 120          # 2 minutes
MAX_LLM_WORKERS: int = 12       # More concurrent requests
```

---

## Environment Variables

### .env File Template

Create `backend/.env`:

```env
# ============ DATABASE ============
DATABASE_URL=postgresql://postgres:admin@localhost:5432/sale_deed_db

# ============ API KEYS ============
GEMINI_API_KEY=your_key_here
GROQ_API_KEY=your_key_here

# ============ LLM BACKEND ============
LLM_BACKEND=gemini
GEMINI_MODEL=gemini-2.5-flash-lite
TEMPERATURE=0.6
MAX_TOKENS=16384
LLM_TIMEOUT=300

# ============ PROCESSING PIPELINE ============
ENABLE_PIPELINE=true
MAX_OCR_WORKERS=2
MAX_LLM_WORKERS=8
STAGE2_QUEUE_SIZE=1
ENABLE_OCR_MULTIPROCESSING=true
OCR_PAGE_WORKERS=1

# ============ OCR SETTINGS ============
TESSERACT_LANG=eng+kan
POPPLER_DPI=300
TARGET_WIDTH=2000
USE_EMBEDDED_OCR=false

# ============ YOLO MODEL ============
YOLO_CONFIDENCE_THRESHOLD=0.88

# ============ LOGGING ============
LOG_LEVEL=INFO
```

### Loading Environment Variables

**Python** (Pydantic auto-loads from .env):
```python
from app.config import settings

print(settings.GEMINI_API_KEY)  # Reads from .env
```

**Manual Loading**:
```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
```

---

## Configuration Presets

### Development Profile

```env
LOG_LEVEL=DEBUG
ENABLE_PIPELINE=true
MAX_OCR_WORKERS=1
MAX_LLM_WORKERS=4
STAGE2_QUEUE_SIZE=1
```

### Production Profile

```env
LOG_LEVEL=INFO
ENABLE_PIPELINE=true
MAX_OCR_WORKERS=2
MAX_LLM_WORKERS=8
STAGE2_QUEUE_SIZE=2
```

### Testing Profile

```env
LOG_LEVEL=DEBUG
ENABLE_PIPELINE=false  # Use legacy mode
MAX_WORKERS=1
```

---

## Troubleshooting Configuration

### Check Current Configuration

```python
# In Python shell or script
from app.config import settings

print(f"Pipeline Mode: {settings.ENABLE_PIPELINE}")
print(f"OCR Workers: {settings.MAX_OCR_WORKERS}")
print(f"LLM Workers: {settings.MAX_LLM_WORKERS}")
print(f"LLM Backend: {settings.LLM_BACKEND}")
```

**Via API**:
```bash
curl http://localhost:8000/api/system/config
```

### Common Configuration Errors

**Error**: LLM API key not set
```
Solution: Add GEMINI_API_KEY to .env file
```

**Error**: Database connection failed
```
Solution: Check DATABASE_URL in .env matches your PostgreSQL setup
```

**Error**: Out of memory during processing
```
Solution: Reduce MAX_OCR_WORKERS to 1, set STAGE2_QUEUE_SIZE to 1
```

**Error**: Tesseract language not found
```
Solution: Install language data for TESSERACT_LANG
```

---

**Document Version**: 1.0
**Last Updated**: December 23, 2024
