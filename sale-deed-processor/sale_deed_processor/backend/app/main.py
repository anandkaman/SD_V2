# backend/app/main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from contextlib import asynccontextmanager
import logging
import sys
from pathlib import Path

from app.config import settings
from app.database import init_db
from app.api.routes import router

# Configure logging with UTF-8 support for Kannada text
import io

# Create UTF-8 StreamHandler for console output
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# Create UTF-8 FileHandler for log file
file_handler = logging.FileHandler('app.log', encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logging.basicConfig(
    level=logging.INFO,
    handlers=[console_handler, file_handler]
)

# Set stdout to UTF-8 mode (for Windows console)
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python < 3.7 fallback
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting Sale Deed Processor API...")
    
    # Create directories
    settings.create_directories()
    logger.info("Directories verified")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    
    # Verify critical files
    if not settings.YOLO_MODEL_PATH.exists():
        logger.warning(f"YOLO model not found at: {settings.YOLO_MODEL_PATH}")
    else:
        logger.info(f"YOLO model found: {settings.YOLO_MODEL_PATH}")
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Sale Deed Processor API...")

# Create FastAPI app with enhanced documentation
app = FastAPI(
    title="Sale Deed Processor API",
    description="""
## SaleDeed Processor - REST API Documentation

A sophisticated API for processing Indian property sale deed documents using AI/ML technologies.

### Features

* **Document Processing**: Upload and process PDF documents with OCR + LLM extraction
* **Vision Processing**: Extract registration fees using computer vision
* **Data Management**: Retrieve, search, and export processed documents
* **Batch Tracking**: Track upload batches and processing status
* **User Management**: Manage user information and support tickets
* **System Monitoring**: Real-time health checks and statistics

### Processing Pipeline

1. **Upload PDFs** → Assign to batch
2. **OCR Stage** → Extract text from PDF pages
3. **LLM Stage** → Extract structured data (30+ fields)
4. **Vision Stage** → Extract registration fee tables
5. **Database** → Store and retrieve results

### Technology Stack

* **Backend**: FastAPI 0.109.0, Python 3.11+
* **Database**: PostgreSQL 13+
* **OCR**: Tesseract 4.1+, Poppler 25.07.0
* **LLM**: Google Gemini, Ollama, Groq
* **Vision**: YOLO (ONNX), Gemini Vision

### Quick Start

1. **Upload PDFs**: `POST /api/upload`
2. **Start Processing**: `POST /api/process/start`
3. **Get Statistics**: `GET /api/process/stats`
4. **View Documents**: `GET /api/documents`
5. **Export Excel**: `GET /api/export/excel`

### API Categories

* **Upload**: Upload PDFs and manage batches
* **Processing**: Start/stop processing, get statistics
* **Vision**: Registration fee extraction
* **Data**: Retrieve documents and export
* **System**: Health checks and configuration
* **User Management**: User info and support tickets

### Authentication

**Current Version**: No authentication required (v1.0 - local desktop application)

**Future Versions**: API keys, JWT tokens

### Rate Limiting

**Current Version**: No rate limiting

**Recommended Client Polling**:
* Processing stats: Every 2 seconds
* System health: Every 10 seconds

### Support

* **Documentation**: `/docs` (Swagger UI), `/redoc` (ReDoc)
* **GitHub**: https://github.com/Nitinkaroshi/salesdeed
* **Version**: 1.0.0
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "SaleDeed Processor Team",
        "url": "https://github.com/Nitinkaroshi/salesdeed",
    },
    license_info={
        "name": "Proprietary",
        "url": "https://github.com/Nitinkaroshi/salesdeed/blob/main/LICENSE",
    },
    openapi_tags=[
        {
            "name": "Upload",
            "description": "Upload PDF files and manage batch sessions"
        },
        {
            "name": "Processing",
            "description": "Start/stop PDF processing and monitor statistics"
        },
        {
            "name": "Vision",
            "description": "Vision-based registration fee extraction"
        },
        {
            "name": "Data",
            "description": "Retrieve processed documents and export to Excel"
        },
        {
            "name": "System",
            "description": "System health checks, configuration, and folder statistics"
        },
        {
            "name": "User Management",
            "description": "User information and support ticket management"
        }
    ]
)

# Add middleware to handle CORS preflight requests
@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    """Handle CORS preflight requests"""
    if request.method == "OPTIONS":
        return Response(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept, Origin",
                "Access-Control-Max-Age": "3600",
            },
        )
    
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = request.headers.get("origin", "*")
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept, Origin"
    response.headers["Access-Control-Expose-Headers"] = "Content-Type, Content-Disposition"
    return response

# CORS middleware for React/Electron frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:4000",  # Electron dev server
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:4000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        "file://*",  # Electron app with file:// protocol
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "Accept", "Origin"],
    expose_headers=["Content-Type", "Content-Disposition"],
    max_age=3600,
)

# Include routes
app.include_router(router, prefix="/api", tags=["api"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Sale Deed Processor API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "api": "operational"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )