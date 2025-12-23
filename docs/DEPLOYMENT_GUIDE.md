# SaleDeed Processor - Deployment Guide v1.0

**Target Platforms**: Windows 10+, macOS 11+, Linux (Ubuntu 20.04+)
**Deployment Type**: Desktop Application (Electron)
**Last Updated**: December 2024

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Development Deployment](#development-deployment)
3. [Production Build](#production-build)
4. [Database Setup](#database-setup)
5. [External Dependencies](#external-dependencies)
6. [Configuration](#configuration)
7. [Testing Deployment](#testing-deployment)
8. [Troubleshooting](#troubleshooting)
9. [Maintenance](#maintenance)

---

## Prerequisites

### System Requirements

**Minimum**:
- CPU: Intel i5 / AMD Ryzen 5 (4 cores)
- RAM: 8 GB
- Storage: 10 GB free space
- OS: Windows 10 / macOS 11 / Ubuntu 20.04

**Recommended**:
- CPU: Intel i7 / AMD Ryzen 7 (8 cores)
- RAM: 16 GB
- Storage: 20 GB SSD
- GPU: NVIDIA GPU with CUDA 11.8+ (optional)

### Software Dependencies

1. **Python 3.11+**
   ```bash
   python --version  # Should show 3.11.x or higher
   ```

2. **Node.js 18+**
   ```bash
   node --version   # Should show v18.x.x or higher
   npm --version    # Should show 9.x.x or higher
   ```

3. **PostgreSQL 13+**
   ```bash
   psql --version   # Should show 13.x or higher
   ```

4. **Tesseract OCR 4.1+**
   ```bash
   tesseract --version   # Should show 4.1.x or higher
   ```

5. **Poppler 25.07+**
   ```bash
   pdfinfo -v   # Should show poppler version
   ```

---

## Development Deployment

### 1. Clone Repository

```bash
git clone https://github.com/Nitinkaroshi/salesdeed.git
cd salesdeed
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
cd sale-deed-processor/sale_deed_processor/backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

#### Configure Environment Variables

Create `.env` file in `backend/` directory:

```env
# Database
DATABASE_URL=postgresql://postgres:admin@localhost:5432/sale_deed_db

# API Keys
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# LLM Configuration
LLM_BACKEND=gemini
GEMINI_MODEL=gemini-2.5-flash-lite

# Processing Settings
ENABLE_PIPELINE=true
MAX_OCR_WORKERS=2
MAX_LLM_WORKERS=8
STAGE2_QUEUE_SIZE=1

# OCR Settings
TESSERACT_LANG=eng+kan
POPPLER_DPI=300
USE_EMBEDDED_OCR=false
```

#### Initialize Database

```bash
# Create database
createdb sale_deed_db

# Or using psql
psql -U postgres
CREATE DATABASE sale_deed_db;
\q

# Run migrations
cd backend
python init_db.py
```

#### Start Backend Server

```bash
cd sale-deed-processor/sale_deed_processor/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend should be running at: `http://localhost:8000`

### 3. Frontend Setup

#### Install Node Dependencies

```bash
cd fronted
npm install
```

#### Start Development Server

**Option 1: Electron Development Mode**
```bash
npm run electron-dev
```

**Option 2: Web Browser Mode**
```bash
npm start
```

Frontend should be running at: `http://localhost:3000`

---

## Production Build

### 1. Build React Application

```bash
cd fronted
npm run build
```

This creates optimized production build in `fronted/build/` directory.

### 2. Create Electron Installer

#### Windows

```bash
cd fronted
npm run dist
```

Output: `dist/SaleDeed Processor Setup 1.0.0.exe` (~100 MB)

#### macOS

```bash
cd fronted
npm run dist -- --mac
```

Output: `dist/SaleDeed Processor-1.0.0.dmg`

#### Linux

```bash
cd fronted
npm run dist -- --linux
```

Output: `dist/SaleDeed Processor-1.0.0.AppImage`

### 3. Build Configuration

**package.json** (electron-builder config):

```json
{
  "build": {
    "appId": "com.salesdeed.processor",
    "productName": "SaleDeed Processor",
    "directories": {
      "buildResources": "public",
      "output": "dist"
    },
    "files": [
      "build/**/*",
      "electron/**/*",
      "node_modules/**/*",
      "package.json"
    ],
    "win": {
      "target": ["nsis"],
      "icon": "public/logo.png"
    },
    "mac": {
      "target": ["dmg"],
      "icon": "public/logo.png",
      "category": "public.app-category.productivity"
    },
    "linux": {
      "target": ["AppImage"],
      "icon": "public/logo.png",
      "category": "Office"
    }
  }
}
```

---

## Database Setup

### PostgreSQL Installation

#### Windows

1. Download PostgreSQL installer from https://www.postgresql.org/download/windows/
2. Run installer (PostgreSQL 13+)
3. Set password for `postgres` user
4. Default port: 5432

#### macOS

```bash
brew install postgresql@13
brew services start postgresql@13
```

#### Linux (Ubuntu)

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Create Database and User

```sql
-- Connect as postgres user
psql -U postgres

-- Create database
CREATE DATABASE sale_deed_db;

-- Create user (optional)
CREATE USER salesdeed_user WITH PASSWORD 'secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE sale_deed_db TO salesdeed_user;

-- Exit
\q
```

### Run Migrations

```bash
cd sale-deed-processor/sale_deed_processor/backend

# Using Python script
python init_db.py

# Or using Alembic
alembic upgrade head
```

### Verify Database

```sql
psql -U postgres -d sale_deed_db

-- List tables
\dt

-- Should show:
-- document_details
-- property_details
-- buyer_details
-- seller_details
-- batch_sessions
-- user_info
-- user_tickets
```

---

## External Dependencies

### 1. Tesseract OCR

#### Windows

1. Download installer: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to `C:\Program Files\Tesseract-OCR\`
3. Add to PATH: `C:\Program Files\Tesseract-OCR\`
4. Download language data:
   - English: `eng.traineddata`
   - Kannada: `kan.traineddata`
   - Place in: `C:\Program Files\Tesseract-OCR\tessdata\`

#### macOS

```bash
brew install tesseract
brew install tesseract-lang  # For Kannada support
```

#### Linux (Ubuntu)

```bash
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-eng tesseract-ocr-kan
```

#### Verify Installation

```bash
tesseract --version
tesseract --list-langs  # Should show eng, kan
```

### 2. Poppler

#### Windows

1. Download from: https://github.com/oschwartz10612/poppler-windows/releases
2. Extract to `C:\poppler\`
3. Add to PATH: `C:\poppler\Library\bin\`

#### macOS

```bash
brew install poppler
```

#### Linux (Ubuntu)

```bash
sudo apt install poppler-utils
```

#### Verify Installation

```bash
pdfinfo -v
pdftoppm -v
```

### 3. YOLO Model

Download YOLO ONNX model:

```bash
cd sale-deed-processor/sale_deed_processor/models
# Ensure table1.19.1.onnx exists
```

If missing, contact team for model file.

### 4. CUDA (Optional - GPU Acceleration)

#### Windows/Linux

1. Download CUDA Toolkit 11.8: https://developer.nvidia.com/cuda-downloads
2. Install NVIDIA drivers (latest)
3. Verify:
   ```bash
   nvidia-smi
   nvcc --version
   ```

#### Python CUDA Support

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 5. Ollama (Optional - Local LLM)

#### Windows/macOS/Linux

```bash
# Download from: https://ollama.ai/download
# Or using script (macOS/Linux)
curl https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama2
ollama serve  # Start server on localhost:11434
```

---

## Configuration

### Backend Configuration (`backend/app/config.py`)

```python
class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:admin@localhost:5432/sale_deed_db"

    # API Keys
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""

    # LLM Backend
    LLM_BACKEND: str = "gemini"  # gemini, ollama, groq
    GEMINI_MODEL: str = "gemini-2.5-flash-lite"

    # Processing
    ENABLE_PIPELINE: bool = True
    MAX_OCR_WORKERS: int = 2
    MAX_LLM_WORKERS: int = 8
    STAGE2_QUEUE_SIZE: int = 1

    # OCR
    TESSERACT_LANG: str = "eng+kan"
    POPPLER_DPI: int = 300
    USE_EMBEDDED_OCR: bool = False
```

### Frontend Configuration (`fronted/src/services/api.js`)

```javascript
const API_BASE_URL = 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000,  // 5 minutes for long operations
  headers: {
    'Content-Type': 'application/json',
  },
});
```

---

## Testing Deployment

### 1. Health Check

```bash
# Backend health
curl http://localhost:8000/health

# Expected: {"status": "ok"}
```

### 2. System Info Check

```bash
curl http://localhost:8000/api/system/info

# Expected:
# {
#   "cuda_available": true/false,
#   "tesseract_available": true,
#   "poppler_available": true,
#   "ollama_connected": true/false,
#   "yolo_model_loaded": true
# }
```

### 3. Test Upload

1. Open Electron app
2. Navigate to Control Panel
3. Upload a sample PDF
4. Verify file appears in `data/newly_uploaded/`

### 4. Test Processing

1. Click "Start Processing"
2. Monitor stats every 2 seconds
3. Verify PDF moves to `data/processed/` or `data/failed/`
4. Check database for records:

```sql
SELECT COUNT(*) FROM document_details;
SELECT COUNT(*) FROM property_details;
```

### 5. Test Data View

1. Navigate to Data View
2. Verify table shows processed documents
3. Test search functionality
4. Test Excel export

---

## Troubleshooting

### Backend Won't Start

**Issue**: `ModuleNotFoundError: No module named 'app'`
```bash
# Solution: Ensure you're in backend directory
cd sale-deed-processor/sale_deed_processor/backend
python -m uvicorn app.main:app --reload
```

**Issue**: Database connection error
```bash
# Solution: Check PostgreSQL is running
# Windows
services.msc  # Find PostgreSQL service

# macOS/Linux
sudo systemctl status postgresql
```

**Issue**: Port 8000 already in use
```bash
# Solution: Use different port or kill process
# Windows
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# macOS/Linux
lsof -ti:8000 | xargs kill -9
```

### Frontend Won't Start

**Issue**: `Error: Cannot find module 'react'`
```bash
# Solution: Reinstall dependencies
cd fronted
rm -rf node_modules package-lock.json
npm install
```

**Issue**: Electron build fails
```bash
# Solution: Clear cache and rebuild
npm run build
rm -rf dist
npm run dist
```

### OCR/Processing Issues

**Issue**: Tesseract not found
```bash
# Solution: Add Tesseract to PATH
# Windows: Add C:\Program Files\Tesseract-OCR\ to System PATH
# Restart terminal/IDE
```

**Issue**: Language data missing
```bash
tesseract --list-langs
# If eng or kan missing, download from:
# https://github.com/tesseract-ocr/tessdata
# Place in tessdata folder
```

**Issue**: Poppler not found
```bash
# Solution: Install and add to PATH
# Windows: Add C:\poppler\Library\bin\ to PATH
```

### Database Issues

**Issue**: Migration failed
```bash
# Solution: Drop and recreate database
dropdb sale_deed_db
createdb sale_deed_db
python init_db.py
```

**Issue**: Permission denied
```bash
# Solution: Grant permissions
psql -U postgres
GRANT ALL PRIVILEGES ON DATABASE sale_deed_db TO postgres;
```

---

## Maintenance

### Backup Database

**Daily Backup**:
```bash
pg_dump -U postgres sale_deed_db > backup_$(date +%Y%m%d).sql
```

**Restore Backup**:
```bash
psql -U postgres sale_deed_db < backup_20241223.sql
```

### Clean Up Old Files

**Manual Cleanup**:
```bash
cd sale-deed-processor/sale_deed_processor/data

# Archive processed files older than 30 days
find processed/ -name "*.pdf" -mtime +30 -exec mv {} archived/ \;

# Clean failed files
rm -rf failed/*.pdf
```

### Update Dependencies

**Python**:
```bash
cd backend
pip list --outdated
pip install --upgrade <package>
pip freeze > requirements.txt
```

**Node.js**:
```bash
cd fronted
npm outdated
npm update
```

### Monitor Logs

**Backend Logs**:
```bash
# Check uvicorn logs
tail -f backend/logs/uvicorn.log
```

**Application Logs**:
```bash
# Check application logs
tail -f backend/logs/app.log
```

### Performance Monitoring

**Database Size**:
```sql
SELECT pg_size_pretty(pg_database_size('sale_deed_db'));
```

**Table Sizes**:
```sql
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## Deployment Checklist

### Pre-Deployment
- [ ] All dependencies installed
- [ ] Database created and migrated
- [ ] Environment variables configured
- [ ] API keys obtained and set
- [ ] Tesseract language data downloaded
- [ ] YOLO model file present

### Development
- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Database connection successful
- [ ] System info shows all green
- [ ] Sample PDF processes successfully

### Production Build
- [ ] React app built successfully (`npm run build`)
- [ ] Electron installer created (`npm run dist`)
- [ ] Installer tested on target OS
- [ ] Application icon displays correctly
- [ ] All features work in packaged app

### Post-Deployment
- [ ] Database backup configured
- [ ] Log rotation enabled
- [ ] Monitoring in place
- [ ] Documentation updated
- [ ] User training completed

---

## Version History

### v1.0 (December 2024)
- Initial production deployment
- Windows installer support
- PostgreSQL 13 integration
- Pipeline processing architecture

---

**Document Version**: 1.0
**Last Updated**: December 23, 2024
