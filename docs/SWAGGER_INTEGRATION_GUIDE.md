# Swagger/OpenAPI Integration Guide

**FastAPI Version**: 0.109.0
**OpenAPI Version**: 3.1.0
**Last Updated**: December 23, 2024

## Table of Contents

1. [Overview](#overview)
2. [Accessing Swagger UI](#accessing-swagger-ui)
3. [Swagger Features](#swagger-features)
4. [Enhanced Configuration](#enhanced-configuration)
5. [Customizing Endpoints](#customizing-endpoints)
6. [Exporting OpenAPI Specification](#exporting-openapi-specification)
7. [Custom Swagger Theme](#custom-swagger-theme)
8. [Best Practices](#best-practices)

---

## Overview

FastAPI automatically generates interactive API documentation using **Swagger UI** and **ReDoc**. The Swagger integration is already built into your SaleDeed Processor API and has been enhanced with detailed descriptions and categorization.

### What is Swagger?

**Swagger (OpenAPI)** is a specification for describing RESTful APIs. It provides:
- **Interactive Documentation**: Try API endpoints directly from the browser
- **Request/Response Examples**: See what data to send and receive
- **Schema Validation**: Automatic validation of requests
- **Code Generation**: Generate client SDKs in multiple languages

---

## Accessing Swagger UI

### 1. Start the Backend Server

```bash
cd sale-deed-processor/sale_deed_processor/backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Open Swagger UI in Browser

Navigate to: **http://localhost:8000/docs**

### 3. Alternative Documentation (ReDoc)

Navigate to: **http://localhost:8000/redoc**

### 4. Download OpenAPI JSON

Navigate to: **http://localhost:8000/openapi.json**

---

## Swagger Features

### Interactive API Testing

1. **Expand an Endpoint**: Click on any endpoint to see details
2. **Try it Out**: Click the "Try it out" button
3. **Fill Parameters**: Enter required parameters or request body
4. **Execute**: Click "Execute" to send the request
5. **View Response**: See the actual response from your API

### Example: Testing Upload Endpoint

1. Go to http://localhost:8000/docs
2. Find `POST /api/upload` under "Upload" section
3. Click "Try it out"
4. Click "Choose Files" to select PDFs
5. Click "Execute"
6. View the response with batch_id

### Endpoint Categories

Your API is organized into 6 categories:

1. **Upload** (Green) - PDF upload and batch management
2. **Processing** (Blue) - Start/stop processing, statistics
3. **Vision** (Purple) - Registration fee extraction
4. **Data** (Orange) - Document retrieval and Excel export
5. **System** (Red) - Health checks and configuration
6. **User Management** (Teal) - User info and tickets

---

## Enhanced Configuration

Your `main.py` has been enhanced with comprehensive OpenAPI metadata:

### Main Configuration

```python
app = FastAPI(
    title="Sale Deed Processor API",
    description="...",  # Markdown-formatted description
    version="1.0.0",
    docs_url="/docs",              # Swagger UI URL
    redoc_url="/redoc",            # ReDoc URL
    openapi_url="/openapi.json",   # OpenAPI spec URL
    contact={
        "name": "SaleDeed Processor Team",
        "url": "https://github.com/Nitinkaroshi/salesdeed",
    },
    license_info={
        "name": "Proprietary",
    },
    openapi_tags=[...]  # Tag descriptions
)
```

### Tag Descriptions

Each API category has a description:

```python
{
    "name": "Upload",
    "description": "Upload PDF files and manage batch sessions"
},
{
    "name": "Processing",
    "description": "Start/stop PDF processing and monitor statistics"
},
# ... more tags
```

---

## Customizing Endpoints

### Adding Better Documentation to Endpoints

Update individual endpoints in `backend/app/api/routes.py`:

```python
@router.post("/upload", response_model=dict, tags=["Upload"])
async def upload_pdfs(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload PDF files for processing

    Uploads one or more PDF files and assigns a unique batch ID.

    **Process**:
    1. Generate unique batch ID
    2. Create BatchSession record
    3. Save files to data/newly_uploaded/
    4. Create DocumentDetail records

    **Example**:
    ```bash
    curl -X POST "http://localhost:8000/api/upload" \\
      -F "files=@document1.pdf"
    ```

    **Returns**:
    - batch_id: Unique identifier
    - uploaded_count: Number of files uploaded
    - files: List of filenames
    """
    # ... endpoint implementation
```

### Adding Response Examples

```python
from fastapi import FastAPI
from pydantic import BaseModel

class UploadResponse(BaseModel):
    success: bool
    batch_id: str
    uploaded_count: int
    files: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "batch_id": "BATCH_20241223_130000_a1b2c3d4",
                "uploaded_count": 2,
                "files": ["document1.pdf", "document2.pdf"]
            }
        }

@router.post("/upload", response_model=UploadResponse, tags=["Upload"])
async def upload_pdfs(...):
    # ...
```

### Adding Query Parameter Descriptions

```python
from fastapi import Query

@router.get("/documents", tags=["Data"])
async def get_all_documents(
    skip: int = Query(0, description="Number of records to skip (pagination offset)"),
    limit: int = Query(100, description="Maximum number of records to return", le=1000),
    db: Session = Depends(get_db)
):
    """Get all documents with pagination"""
    # ...
```

---

## Exporting OpenAPI Specification

### 1. Download JSON Specification

```bash
curl http://localhost:8000/openapi.json > openapi.json
```

### 2. Convert to YAML (Optional)

Install converter:
```bash
pip install pyyaml
```

Convert:
```python
import json
import yaml

# Read JSON
with open('openapi.json', 'r') as f:
    spec = json.load(f)

# Write YAML
with open('openapi.yaml', 'w') as f:
    yaml.dump(spec, f, default_flow_style=False)
```

### 3. Import into Postman

1. Open Postman
2. Click "Import"
3. Select `openapi.json`
4. All endpoints will be imported as a collection

### 4. Generate Client SDK

Using **openapi-generator**:

```bash
# Install
npm install -g @openapitools/openapi-generator-cli

# Generate Python client
openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g python \
  -o ./python-client

# Generate JavaScript client
openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g javascript \
  -o ./js-client
```

---

## Custom Swagger Theme

### Add Custom CSS to Swagger UI

Create a custom HTML template:

**File**: `backend/app/static/swagger-ui-custom.html`

```html
<!DOCTYPE html>
<html>
<head>
    <title>SaleDeed Processor API - Swagger UI</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@4/swagger-ui.css">
    <style>
        /* Custom theme colors */
        .swagger-ui .topbar {
            background-color: #1e3a8a;
        }
        .swagger-ui .info .title {
            color: #1e3a8a;
        }
        /* Add your custom styles */
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@4/swagger-ui-bundle.js"></script>
    <script>
        window.onload = function() {
            window.ui = SwaggerUIBundle({
                url: "/openapi.json",
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.SwaggerUIStandalonePreset
                ]
            });
        }
    </script>
</body>
</html>
```

**Mount static files** in `main.py`:

```python
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="app/static"), name="static")
```

---

## Integrating with Your PDF Documentation

### Option 1: Link to Swagger UI

Add to your `docs/API_DOCUMENTATION.md`:

```markdown
## Live API Documentation

For interactive API testing, visit the Swagger UI:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json
```

### Option 2: Embed Swagger in HTML

Create `docs/api-interactive.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>SaleDeed API - Interactive Documentation</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@4/swagger-ui.css">
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@4/swagger-ui-bundle.js"></script>
    <script>
        window.onload = function() {
            window.ui = SwaggerUIBundle({
                url: "http://localhost:8000/openapi.json",
                dom_id: '#swagger-ui',
            });
        }
    </script>
</body>
</html>
```

Open in browser: `file:///e:/salesdeed/docs/api-interactive.html`

### Option 3: Generate Static HTML from OpenAPI

Using **redoc-cli**:

```bash
# Install
npm install -g redoc-cli

# Generate static HTML
redoc-cli bundle http://localhost:8000/openapi.json \
  -o docs/api-static.html \
  --title "SaleDeed API Documentation"
```

This creates a single HTML file with all API documentation.

---

## Best Practices

### 1. Write Descriptive Docstrings

```python
@router.get("/documents/{document_id}", tags=["Data"])
async def get_document(document_id: str, db: Session = Depends(get_db)):
    """
    Retrieve a specific document by ID

    Fetches complete document details including property info, buyers, and sellers.

    Args:
        document_id: Unique document identifier (extracted from PDF filename)

    Returns:
        DocumentDetailSchema with all related records

    Raises:
        404: Document not found

    Example:
        GET /api/documents/DOC_2024_001
    """
    # ...
```

### 2. Use Response Models

```python
@router.post("/upload", response_model=UploadResponse, tags=["Upload"])
async def upload_pdfs(...):
    # Response automatically validated and documented
    return UploadResponse(
        success=True,
        batch_id=batch_id,
        uploaded_count=len(uploaded_files),
        files=uploaded_files
    )
```

### 3. Add Examples to Schemas

```python
class DocumentDetailSchema(BaseModel):
    document_id: str
    transaction_date: Optional[date] = None

    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "DOC_2024_001",
                "transaction_date": "2024-01-15"
            }
        }
```

### 4. Use Enum for Fixed Values

```python
from enum import Enum

class TicketStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"

class UserTicketSchema(BaseModel):
    status: TicketStatus  # Automatically documented with dropdown
```

### 5. Document Error Responses

```python
@router.get("/documents/{document_id}",
    responses={
        200: {"description": "Document found"},
        404: {"description": "Document not found"},
        500: {"description": "Server error"}
    }
)
async def get_document(...):
    # ...
```

---

## Swagger UI Screenshots

### Main Interface

When you visit http://localhost:8000/docs, you'll see:

```
┌─────────────────────────────────────────────────────────┐
│  Sale Deed Processor API                        v1.0.0  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Description with markdown formatting                   │
│  • Features                                             │
│  • Technology Stack                                     │
│  • Quick Start                                          │
│                                                          │
├─────────────────────────────────────────────────────────┤
│  ▼ Upload                                               │
│    POST  /api/upload          Upload PDF files         │
│    GET   /api/batches         Get all batches          │
│                                                          │
│  ▼ Processing                                           │
│    POST  /api/process/start   Start processing         │
│    POST  /api/process/stop    Stop processing          │
│    GET   /api/process/stats   Get statistics           │
│    ...                                                  │
│                                                          │
│  ▼ Data                                                 │
│    GET   /api/documents       Get all documents        │
│    GET   /api/export/excel    Export to Excel          │
│    ...                                                  │
└─────────────────────────────────────────────────────────┘
```

### Testing an Endpoint

```
┌─────────────────────────────────────────────────────────┐
│  POST /api/upload                                       │
│                                                          │
│  Upload PDF files for processing                        │
│                                                          │
│  [ Try it out ]                                         │
│                                                          │
│  Parameters:                                            │
│    files* (required)                                    │
│    [ Choose Files ]                                     │
│                                                          │
│  [ Execute ]                                            │
│                                                          │
│  Response:                                              │
│  {                                                      │
│    "success": true,                                     │
│    "batch_id": "BATCH_20241223_130000_a1b2c3d4",       │
│    "uploaded_count": 2,                                 │
│    "files": ["doc1.pdf", "doc2.pdf"]                   │
│  }                                                      │
└─────────────────────────────────────────────────────────┘
```

---

## Accessing Swagger UI

### From Desktop Application

Add a "View API Docs" button in your React frontend:

```javascript
const openApiDocs = () => {
  // Open Swagger UI in default browser
  window.open('http://localhost:8000/docs', '_blank');
};

<button onClick={openApiDocs}>
  View API Documentation
</button>
```

### From Electron Menu

Add menu item in `electron/main.js`:

```javascript
const { Menu, shell } = require('electron');

const template = [
  {
    label: 'Help',
    submenu: [
      {
        label: 'API Documentation',
        click: () => {
          shell.openExternal('http://localhost:8000/docs');
        }
      },
      {
        label: 'API Reference (ReDoc)',
        click: () => {
          shell.openExternal('http://localhost:8000/redoc');
        }
      }
    ]
  }
];

const menu = Menu.buildFromTemplate(template);
Menu.setApplicationMenu(menu);
```

---

## Summary

### What You Have

✅ **Swagger UI**: Interactive API testing at http://localhost:8000/docs
✅ **ReDoc**: Beautiful API docs at http://localhost:8000/redoc
✅ **OpenAPI JSON**: Machine-readable spec at http://localhost:8000/openapi.json
✅ **Enhanced Descriptions**: Detailed API information
✅ **Categorized Endpoints**: Organized by function (Upload, Processing, etc.)
✅ **Request/Response Examples**: Sample data for all endpoints

### What You Can Do

1. **Test APIs Interactively**: Try endpoints without writing code
2. **Generate Client SDKs**: Auto-generate API clients in any language
3. **Import to Postman**: One-click import of all endpoints
4. **Export to Static HTML**: Create standalone documentation
5. **Share with Team**: Send link to http://localhost:8000/docs

### Next Steps

1. Visit http://localhost:8000/docs to see enhanced Swagger UI
2. Try testing some endpoints interactively
3. Export OpenAPI JSON for use in other tools
4. Consider adding more detailed examples to individual endpoints

---

**Document Version**: 1.0
**Last Updated**: December 23, 2024
