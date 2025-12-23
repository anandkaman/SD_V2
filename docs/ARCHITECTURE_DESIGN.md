# SaleDeed Processor - Architecture Design Document v1.0

**System Type**: Desktop Application (Electron + FastAPI)
**Architecture Pattern**: Client-Server with Pipeline Processing
**Last Updated**: December 2024

## Table of Contents

1. [System Overview](#system-overview)
2. [High-Level Architecture](#high-level-architecture)
3. [Component Architecture](#component-architecture)
4. [Processing Pipeline](#processing-pipeline)
5. [Data Flow](#data-flow)
6. [Technology Stack](#technology-stack)
7. [Design Patterns](#design-patterns)
8. [Scalability & Performance](#scalability--performance)
9. [Security Architecture](#security-architecture)
10. [Deployment Architecture](#deployment-architecture)

---

## System Overview

### Purpose
SaleDeed Processor is a desktop application that automates the extraction of structured data from Indian property sale deed PDF documents using AI/ML technologies.

### Key Components
1. **Frontend**: React + Electron desktop UI
2. **Backend**: FastAPI server with async processing
3. **Database**: PostgreSQL for structured data storage
4. **Processing Pipeline**: 2-stage OCR + LLM extraction
5. **Vision Module**: Computer vision for registration fee extraction

### Architecture Principles
- **Separation of Concerns**: Frontend, backend, and processing layers are decoupled
- **Async Processing**: Long-running tasks don't block the UI
- **Pipeline Architecture**: Multi-stage processing with parallel workers
- **Modular Design**: Pluggable LLM backends and OCR engines
- **Scalability**: Configurable worker pools for horizontal scaling

---

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │          Electron Desktop Application                      │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │ │
│  │  │ Control Panel│  │  Data View   │  │  System Health   │ │ │
│  │  │  (Upload &   │  │ (Excel-like  │  │   (Footer)       │ │ │
│  │  │  Processing) │  │   Table)     │  │                  │ │ │
│  │  └──────────────┘  └──────────────┘  └──────────────────┘ │ │
│  │           React 18 + React Router + Theme Context         │ │
│  └────────────────────────────────────────────────────────────┘ │
└───────────────────────────┬──────────────────────────────────────┘
                            │ HTTP/REST API (Port 3000 → 8000)
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                             │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │               FastAPI Backend (Port 8000)                  │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │ │
│  │  │  API Routes  │  │  Processors  │  │    Services      │ │ │
│  │  │  (30+ EPs)   │→ │  (Pipeline)  │→ │  OCR/LLM/Vision  │ │ │
│  │  └──────────────┘  └──────────────┘  └──────────────────┘ │ │
│  │           SQLAlchemy ORM + Background Tasks               │ │
│  └────────────────────────────────────────────────────────────┘ │
└───────────────────────────┬──────────────────────────────────────┘
                            │ SQL Queries
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│                     DATA LAYER                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              PostgreSQL Database (Port 5432)               │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────┐ │ │
│  │  │Documents │  │Properties│  │Buyers/   │  │  Batches  │ │ │
│  │  │          │  │          │  │Sellers   │  │  & Users  │ │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └───────────┘ │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 EXTERNAL SERVICES LAYER                          │
│  ┌────────────┐  ┌───────────┐  ┌──────────┐  ┌──────────────┐ │
│  │ Tesseract  │  │  Google   │  │  Ollama  │  │     YOLO     │ │
│  │    OCR     │  │  Gemini   │  │   LLM    │  │  (ONNX RT)   │ │
│  └────────────┘  └───────────┘  └──────────┘  └──────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### Frontend Components

```
fronted/
├── electron/
│   └── main.js                 # Electron main process
├── src/
│   ├── components/
│   │   ├── Layout.js           # Main layout wrapper
│   │   └── Footer.js           # System health display
│   ├── pages/
│   │   ├── ControlPanel.js     # PDF upload & processing
│   │   └── DataView.js         # Excel-like data table
│   ├── services/
│   │   └── api.js              # Axios HTTP client
│   ├── context/
│   │   └── ThemeContext.js     # Theme state management
│   ├── styles/                 # CSS files
│   ├── App.js                  # Main app component
│   └── index.js                # React entry point
└── package.json
```

**Component Hierarchy**:
```
App
├── ThemeProvider
│   └── Layout
│       ├── Header + Navigation
│       ├── Page Content
│       │   ├── ControlPanel (Route: /control-panel)
│       │   └── DataView (Route: /data)
│       └── Footer (System Health)
```

---

### Backend Components

```
backend/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration settings
│   ├── database.py             # DB connection & session
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── api/
│   │   └── routes.py           # REST API endpoints
│   ├── services/               # Business logic
│   │   ├── ocr_service.py      # Tesseract OCR
│   │   ├── llm_service*.py     # LLM integrations
│   │   ├── vision_service*.py  # Vision models
│   │   ├── yolo_detector.py    # YOLO table detection
│   │   ├── pdf_processor*.py   # PDF processing
│   │   └── validation_service.py
│   ├── workers/                # Batch processors
│   │   ├── batch_processor.py         # V1 (Legacy)
│   │   ├── pipeline_processor_v2.py   # V2 (Pipeline)
│   │   └── vision_batch_processor.py
│   └── utils/
│       ├── file_handler.py     # File operations
│       └── prompts.py          # LLM prompts
└── requirements.txt
```

---

## Processing Pipeline

### Pipeline Architecture (V2)

```
┌────────────────────────────────────────────────────────────────────┐
│                       STAGE 1: OCR EXTRACTION                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    OCR Worker Pool                            │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │  │
│  │  │  Worker 1   │  │  Worker 2   │  │  Worker N   │          │  │
│  │  │             │  │             │  │             │          │  │
│  │  │ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │          │  │
│  │  │ │ PDF →   │ │  │ │ PDF →   │ │  │ │ PDF →   │ │          │  │
│  │  │ │ Images  │ │  │ │ Images  │ │  │ │ Images  │ │          │  │
│  │  │ └─────────┘ │  │ └─────────┘ │  │ └─────────┘ │          │  │
│  │  │      ↓      │  │      ↓      │  │      ↓      │          │  │
│  │  │ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │          │  │
│  │  │ │Tesseract│ │  │ │Tesseract│ │  │ │Tesseract│ │          │  │
│  │  │ │  OCR    │ │  │ │  OCR    │ │  │ │  OCR    │ │          │  │
│  │  │ └─────────┘ │  │ └─────────┘ │  │ └─────────┘ │          │  │
│  │  │      ↓      │  │      ↓      │  │      ↓      │          │  │
│  │  │  Raw Text  │  │  Raw Text  │  │  Raw Text  │          │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘          │  │
│  └─────────────────────┬──────────────────────────────────────────┘  │
└────────────────────────┼──────────────────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │   Bounded Queue (Size: 1-10)   │ ← Memory-safe queueing
         │  Stage1Result objects          │
         └───────────────┬───────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────────┐
│                     STAGE 2: LLM EXTRACTION                         │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    LLM Worker Pool                            │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │  │
│  │  │  Worker 1   │  │  Worker 2   │  │  Worker N   │          │  │
│  │  │             │  │             │  │             │          │  │
│  │  │ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │          │  │
│  │  │ │ Raw     │ │  │ │ Raw     │ │  │ │ Raw     │ │          │  │
│  │  │ │ Text    │ │  │ │ Text    │ │  │ │ Text    │ │          │  │
│  │  │ └─────────┘ │  │ └─────────┘ │  │ └─────────┘ │          │  │
│  │  │      ↓      │  │      ↓      │  │      ↓      │          │  │
│  │  │ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │          │  │
│  │  │ │ Gemini  │ │  │ │ Gemini  │ │  │ │ Gemini  │ │          │  │
│  │  │ │   LLM   │ │  │ │   LLM   │ │  │ │   LLM   │ │          │  │
│  │  │ └─────────┘ │  │ └─────────┘ │  │ └─────────┘ │          │  │
│  │  │      ↓      │  │      ↓      │  │      ↓      │          │  │
│  │  │ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │          │  │
│  │  │ │ Validate│ │  │ │ Validate│ │  │ │ Validate│ │          │  │
│  │  │ │   JSON  │ │  │ │   JSON  │ │  │ │   JSON  │ │          │  │
│  │  │ └─────────┘ │  │ └─────────┘ │  │ └─────────┘ │          │  │
│  │  │      ↓      │  │      ↓      │  │      ↓      │          │  │
│  │  │  Save to DB│  │  Save to DB│  │  Save to DB│          │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘          │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
```

### Pipeline Characteristics

**Stage 1 (OCR)**:
- **Input**: PDF files
- **Workers**: 1-2 (Memory-intensive)
- **Processing**:
  1. PDF → Images (Poppler at 300 DPI)
  2. Image → Text (Tesseract eng+kan)
  3. Multiprocessing for page-level parallelism
- **Output**: Stage1Result (document_id, text, file_path)

**Stage 2 (LLM)**:
- **Input**: Stage1Result from queue
- **Workers**: 4-8 (I/O-intensive)
- **Processing**:
  1. Text → LLM (Gemini with structured prompt)
  2. Parse JSON response
  3. Validate extracted data
  4. Save to database
- **Output**: DocumentDetail + related records

**Queue Management**:
- Bounded queue (1-10 items) prevents memory overflow
- Producer (Stage 1) blocks when queue full
- Consumer (Stage 2) blocks when queue empty

---

## Data Flow

### Upload Flow

```
User → Electron → React Upload Component
                      ↓ FormData (multipart/form-data)
                FastAPI /api/upload
                      ↓
                  1. Generate Batch ID (BATCH_YYYYMMDD_HHMMSS_UUID)
                  2. Create BatchSession record
                  3. Save files to data/newly_uploaded/
                  4. Create DocumentDetail records
                      ↓
                Return: { batch_id, uploaded_count, files[] }
```

### Processing Flow

```
User → Click "Start Processing" → React → FastAPI /api/process/start
                                             ↓
                                  1. Update BatchSession (processing_started_at)
                                  2. Start PipelineBatchProcessor (BackgroundTask)
                                             ↓
                        ┌─────────────────────────────────────────┐
                        │  Stage 1: OCR (ThreadPoolExecutor)     │
                        │  ┌──────────────────────────────────┐  │
                        │  │ For each PDF:                    │  │
                        │  │  1. Convert to images            │  │
                        │  │  2. OCR each page                │  │
                        │  │  3. Put Stage1Result in queue    │  │
                        │  └──────────────────────────────────┘  │
                        └─────────────────────────────────────────┘
                                             ↓ Queue
                        ┌─────────────────────────────────────────┐
                        │  Stage 2: LLM (ThreadPoolExecutor)     │
                        │  ┌──────────────────────────────────┐  │
                        │  │ For each Stage1Result:           │  │
                        │  │  1. Send text to LLM             │  │
                        │  │  2. Parse JSON response          │  │
                        │  │  3. Save to database             │  │
                        │  │  4. Move PDF to processed/failed │  │
                        │  └──────────────────────────────────┘  │
                        └─────────────────────────────────────────┘
                                             ↓
                                    Database (PostgreSQL)
```

### Data Retrieval Flow

```
User → Click "Data View" → React → FastAPI /api/documents?skip=0&limit=100
                                        ↓
                              SQLAlchemy Query with joinedload()
                                        ↓
                              PostgreSQL (eager load relationships)
                                        ↓
                              JSON Response (DocumentDetailSchema[])
                                        ↓
                              React Table Rendering
```

---

## Technology Stack

### Frontend Stack
- **UI Framework**: React 18.2.0
- **Desktop**: Electron 28.0.0
- **Routing**: React Router DOM 6.20.0
- **HTTP**: Axios 1.6.2
- **State**: React Context API
- **Styling**: CSS (BEM methodology)
- **Icons**: Lucide React 0.294.0

### Backend Stack
- **Web Framework**: FastAPI 0.109.0
- **Server**: Uvicorn 0.27.0 (ASGI)
- **ORM**: SQLAlchemy 2.0.25
- **Validation**: Pydantic 2.5.3
- **Database**: PostgreSQL 13+
- **Migration**: Alembic 1.13.1

### AI/ML Stack
- **OCR**: Tesseract 4.1+ (eng+kan)
- **PDF**: Poppler 25.07.0, pdfplumber 0.10.3, PyMuPDF 1.26.7
- **LLM**: Google Gemini 2.5 Flash Lite (primary), Ollama/Groq (fallback)
- **Vision**: Gemini Vision API
- **Object Detection**: YOLO (ONNX Runtime 1.16.3)
- **Image Processing**: OpenCV 4.9.0

### Data Processing
- **Excel**: openpyxl (server), xlsx (client)
- **Dataframes**: Pandas 2.1.4
- **Numerical**: NumPy 1.26.3

---

## Design Patterns

### 1. Factory Pattern
**Usage**: LLM Service instantiation

```python
# llm_service_factory.py
def get_llm_service(backend: str) -> BaseLLMService:
    if backend == "gemini":
        return GeminiLLMService()
    elif backend == "ollama":
        return OllamaLLMService()
    elif backend == "groq":
        return GroqLLMService()
    # ... other backends
```

### 2. Repository Pattern
**Usage**: Database operations

```python
# Database access through SQLAlchemy ORM
def get_document(db: Session, document_id: str):
    return db.query(DocumentDetail).filter(
        DocumentDetail.document_id == document_id
    ).first()
```

### 3. Dependency Injection
**Usage**: FastAPI route dependencies

```python
@router.get("/documents")
async def get_all_documents(db: Session = Depends(get_db)):
    return db.query(DocumentDetail).all()
```

### 4. Pipeline Pattern
**Usage**: Multi-stage document processing

```python
# Stage 1: OCR
ocr_result = ocr_service.extract_text(pdf_path)

# Stage 2: LLM
llm_result = llm_service.extract_structured_data(ocr_result.text)

# Stage 3: Validation & Save
validation_service.validate_and_save(llm_result, db)
```

### 5. Worker Pool Pattern
**Usage**: Parallel processing

```python
with ThreadPoolExecutor(max_workers=ocr_workers) as executor:
    futures = [executor.submit(process_pdf, pdf) for pdf in pdfs]
    for future in as_completed(futures):
        result = future.result()
```

---

## Scalability & Performance

### Horizontal Scaling
- **OCR Workers**: 1-2 (limited by memory ~500MB-1GB each)
- **LLM Workers**: 4-8 (limited by API rate limits)
- **Vision Workers**: 1 (sequential processing)

### Memory Management
- Image resizing to 2000px width (optimized for Indic scripts)
- Bounded queues (1-10 items) prevent memory overflow
- Automatic cleanup of processed images

### Performance Optimizations
1. **Async I/O**: FastAPI async endpoints
2. **Connection Pooling**: SQLAlchemy pool size 5, max overflow 10
3. **Eager Loading**: joinedload() prevents N+1 queries
4. **Pagination**: offset/limit for large result sets
5. **Indexes**: Foreign keys and frequently queried columns

### Caching Strategy
- **Frontend**: No caching (real-time data)
- **Backend**: No caching (v1.0, planned for v2.0)
- **Database**: Query result caching (PostgreSQL shared buffers)

---

## Security Architecture

### Current Security (v1.0)
- **No Authentication**: Local desktop application
- **Local Database**: PostgreSQL on localhost
- **File System**: Direct file access
- **API**: No CORS restrictions

### Planned Security (v2.0)
- **Authentication**: API keys, JWT tokens
- **Authorization**: Role-based access control
- **Encryption**: TLS for API, encrypted database connections
- **Input Validation**: Pydantic schemas, file type validation
- **Rate Limiting**: Per-IP rate limits

### Data Privacy
- **PII Handling**: Aadhaar, PAN stored as plain text (local only)
- **API Keys**: Stored in .env file (not committed)
- **Database**: Local PostgreSQL (not exposed externally)

---

## Deployment Architecture

### Development Environment
```
Developer Machine
├── VSCode / IDE
├── PostgreSQL (localhost:5432)
├── Tesseract + Poppler (system PATH)
├── Python 3.11 (backend virtual env)
├── Node.js 18 (frontend)
└── Ollama (optional, localhost:11434)
```

### Production Deployment (Desktop)
```
User Machine (Windows)
├── SaleDeed Processor.exe (Electron packaged app)
│   ├── React Frontend (bundled)
│   ├── Electron Runtime
│   └── FastAPI Backend (bundled with PyInstaller)
├── PostgreSQL (local installation)
├── Tesseract OCR (bundled or system install)
├── Poppler (bundled in app directory)
└── YOLO Model (table1.19.1.onnx, bundled)
```

### Cloud Deployment (Future)
```
Cloud Infrastructure
├── Frontend: Static hosting (S3 + CloudFront)
├── Backend: Container orchestration (ECS/K8s)
│   ├── FastAPI pods (auto-scaling 2-10)
│   └── Worker pods (OCR/LLM pools)
├── Database: RDS PostgreSQL (Multi-AZ)
├── Storage: S3 for PDF files
└── LLM: Gemini API (external), Ollama (self-hosted)
```

---

## Architectural Decisions

### Why Electron + FastAPI?
- **Electron**: Cross-platform desktop without native code
- **FastAPI**: Async Python, automatic OpenAPI docs, fast development
- **Separation**: Frontend/backend can be deployed separately in future

### Why PostgreSQL?
- **Relational Data**: Documents, properties, buyers/sellers have clear relationships
- **ACID Compliance**: Data integrity for financial records
- **JSON Support**: Flexible storage for LLM responses
- **Performance**: Better than SQLite for concurrent access

### Why Pipeline Architecture?
- **Parallelism**: OCR and LLM can run concurrently
- **Memory Efficiency**: Bounded queue prevents overflow
- **Scalability**: Worker pools can be tuned independently
- **Fault Tolerance**: Failed stages don't crash entire process

### Why Multiple LLM Backends?
- **Flexibility**: Switch backends based on cost/performance
- **Reliability**: Fallback if primary LLM is down
- **Testing**: Compare accuracy across models
- **Privacy**: Option for local LLM (Ollama)

---

## Future Architecture Enhancements

### Version 2.0 Roadmap
1. **Microservices**: Split OCR, LLM, Vision into separate services
2. **Message Queue**: RabbitMQ/Redis for inter-service communication
3. **API Gateway**: Single entry point with routing
4. **Monitoring**: Prometheus + Grafana for metrics
5. **Logging**: Centralized logging with ELK stack
6. **Caching**: Redis for frequent queries
7. **CDN**: Static asset delivery
8. **Load Balancer**: Distribute traffic across backend instances

---

**Document Version**: 1.0
**Last Updated**: December 23, 2024
