# SaleDeed Processor - API Documentation v1.0

**Base URL**: `http://localhost:8000/api`

**Last Updated**: December 2024

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Common Response Formats](#common-response-formats)
4. [Upload Endpoints](#upload-endpoints)
5. [Processing Endpoints](#processing-endpoints)
6. [Vision Processing Endpoints](#vision-processing-endpoints)
7. [Data Retrieval Endpoints](#data-retrieval-endpoints)
8. [System Information Endpoints](#system-information-endpoints)
9. [User Management Endpoints](#user-management-endpoints)
10. [Support Ticket Endpoints](#support-ticket-endpoints)
11. [Error Handling](#error-handling)
12. [Rate Limiting](#rate-limiting)

---

## Overview

The SaleDeed Processor API provides endpoints for:
- Uploading PDF documents
- Processing PDFs with OCR and LLM extraction
- Vision-based registration fee extraction
- Retrieving processed data
- System health monitoring
- User and batch management
- Support ticket system

### API Features
- **RESTful Design**: Standard HTTP methods (GET, POST, PATCH)
- **JSON Responses**: All responses in JSON format
- **Pagination Support**: For large datasets
- **Batch Processing**: Track uploads with unique batch IDs
- **Background Tasks**: Long-running processes use FastAPI BackgroundTasks
- **Streaming Responses**: For file downloads (Excel, ZIP)

---

## Authentication

**Current Version**: No authentication required (v1.0)

**Future Versions**: Will support:
- API Key authentication
- JWT tokens
- OAuth 2.0

---

## Common Response Formats

### Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { ... }
}
```

### Error Response
```json
{
  "detail": "Error message describing what went wrong"
}
```

### HTTP Status Codes
- `200 OK`: Request successful
- `400 Bad Request`: Invalid parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## Upload Endpoints

### 1. Upload PDF Files

**Endpoint**: `POST /api/upload`

**Description**: Upload one or more PDF files for processing. Automatically creates a unique batch ID and database records.

**Request**:
- **Content-Type**: `multipart/form-data`
- **Body**: Form data with file(s)

```bash
curl -X POST "http://localhost:8000/api/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@document1.pdf" \
  -F "files=@document2.pdf"
```

**Response**: `200 OK`
```json
{
  "success": true,
  "uploaded_count": 2,
  "files": [
    "document1.pdf",
    "document2.pdf"
  ],
  "batch_id": "BATCH_20241223_130000_a1b2c3d4"
}
```

**Notes**:
- Only `.pdf` files are accepted
- Batch ID format: `BATCH_YYYYMMDD_HHMMSS_UUID`
- First document name used as batch name
- Creates `DocumentDetail` records with batch association
- Files saved to `data/newly_uploaded/` directory

**Error Responses**:
- `500`: Upload failed (disk full, permission issues, etc.)

---

### 2. Get All Batches

**Endpoint**: `GET /api/batches`

**Description**: Retrieve all batch sessions with document counts and metadata.

**Request**:
```bash
curl "http://localhost:8000/api/batches"
```

**Response**: `200 OK`
```json
[
  {
    "batch_id": "BATCH_20241223_130000_a1b2c3d4",
    "batch_name": "Sale_Deed_2024_001",
    "total_count": 15,
    "created_at": "2024-12-23T13:00:00",
    "status": "completed"
  },
  {
    "batch_id": "BATCH_20241223_140000_e5f6g7h8",
    "batch_name": "Sale_Deed_2024_002",
    "total_count": 8,
    "created_at": "2024-12-23T14:00:00",
    "status": "processing"
  }
]
```

**Batch Status Values**:
- `pending`: Uploaded but not started processing
- `processing`: Currently being processed
- `completed`: Processing finished

---

## Processing Endpoints

### 3. Start Processing

**Endpoint**: `POST /api/process/start`

**Description**: Start batch processing of uploaded PDFs. Supports both Pipeline Mode (V2) and Legacy Mode (V1).

**Request Body** (JSON):
```json
{
  "max_workers": 2,
  "ocr_workers": 2,
  "llm_workers": 6,
  "stage2_queue_size": 1,
  "enable_ocr_multiprocessing": true,
  "ocr_page_workers": 1
}
```

**Parameters**:
- `max_workers` (int, optional): Total workers for Legacy Mode (1-20). Default: 2
- `ocr_workers` (int, optional): OCR workers for Pipeline Mode (1-20). Default: from config
- `llm_workers` (int, optional): LLM workers for Pipeline Mode (1-20). Default: from config
- `stage2_queue_size` (int, optional): Bounded queue size (1-10). Default: 1
- `enable_ocr_multiprocessing` (bool, optional): Enable OCR multiprocessing. Default: from config
- `ocr_page_workers` (int, optional): Page-level OCR workers (1-8). Default: from config

**Request** (Pipeline Mode):
```bash
curl -X POST "http://localhost:8000/api/process/start" \
  -H "Content-Type: application/json" \
  -d '{
    "ocr_workers": 2,
    "llm_workers": 6,
    "stage2_queue_size": 1
  }'
```

**Response**: `200 OK` (Pipeline Mode)
```json
{
  "success": true,
  "message": "Started processing 15 PDFs with 2 OCR + 6 LLM workers",
  "total_files": 15,
  "ocr_workers": 2,
  "llm_workers": 6,
  "stage2_queue_size": 1,
  "enable_ocr_multiprocessing": true,
  "ocr_page_workers": 1,
  "pipeline_mode": true
}
```

**Response**: `200 OK` (Legacy Mode)
```json
{
  "success": true,
  "message": "Started processing 15 PDFs with 2 workers",
  "total_files": 15,
  "max_workers": 2,
  "pipeline_mode": false
}
```

**Error Responses**:
- `400`: Processing already running
- `400`: Invalid worker count (must be 1-20)
- `400`: Invalid queue size (must be 1-10)
- `400`: Invalid OCR page workers (must be 1-8)

**Notes**:
- Updates batch session with `processing_started_at` timestamp
- Processing runs in background (non-blocking)
- Check `/process/stats` for progress

---

### 4. Stop Processing

**Endpoint**: `POST /api/process/stop`

**Description**: Stop ongoing PDF processing. Completes current tasks gracefully.

**Request**:
```bash
curl -X POST "http://localhost:8000/api/process/stop"
```

**Response**: `200 OK`
```json
{
  "success": true,
  "message": "Processing stopped. 5 PDF(s) remaining in newly uploaded folder.",
  "stopped_count": 5
}
```

**Error Response**:
```json
{
  "success": false,
  "message": "No batch processing is running"
}
```

---

### 5. Get Processing Statistics

**Endpoint**: `GET /api/process/stats`

**Description**: Real-time processing statistics. Poll every 2 seconds for updates.

**Request**:
```bash
curl "http://localhost:8000/api/process/stats"
```

**Response**: `200 OK` (Pipeline Mode)
```json
{
  "total": 15,
  "processed": 8,
  "successful": 7,
  "failed": 1,
  "is_running": true,
  "active_workers": 8,
  "current_file": "document_009.pdf",
  "ocr_workers": 2,
  "llm_workers": 6,
  "ocr_active": 2,
  "llm_active": 5,
  "in_queue": 3,
  "pipeline_mode": true
}
```

**Response**: `200 OK` (Legacy Mode)
```json
{
  "total": 15,
  "processed": 8,
  "successful": 7,
  "failed": 1,
  "is_running": true,
  "active_workers": 2,
  "current_file": "document_009.pdf",
  "pipeline_mode": false
}
```

**Field Descriptions**:
- `total`: Total PDFs in batch
- `processed`: Number processed (successful + failed)
- `successful`: Successfully processed PDFs
- `failed`: Failed PDFs
- `is_running`: Processing active
- `active_workers`: Total active workers
- `current_file`: File currently being processed
- `ocr_workers`: Configured OCR workers (Pipeline Mode)
- `llm_workers`: Configured LLM workers (Pipeline Mode)
- `ocr_active`: Active OCR workers (Pipeline Mode)
- `llm_active`: Active LLM workers (Pipeline Mode)
- `in_queue`: Items in Stage 2 queue (Pipeline Mode)

---

### 6. Toggle Embedded OCR Mode

**Endpoint**: `POST /api/process/toggle-embedded-ocr?enabled={boolean}`

**Description**: Switch between PyMuPDF embedded OCR and Poppler+Tesseract OCR.

**Request**:
```bash
curl -X POST "http://localhost:8000/api/process/toggle-embedded-ocr?enabled=true"
```

**Response**: `200 OK`
```json
{
  "success": true,
  "message": "Embedded OCR mode enabled",
  "use_embedded_ocr": true,
  "ocr_mode": "PyMuPDF (Embedded OCR)"
}
```

**OCR Modes**:
- `true`: PyMuPDF embedded OCR (faster, requires embedded text)
- `false`: Poppler + Tesseract (slower, works with scanned PDFs)

---

### 7. Rerun Failed PDFs

**Endpoint**: `POST /api/process/rerun-failed`

**Description**: Move all failed PDFs back to `newly_uploaded` folder for reprocessing.

**Request**:
```bash
curl -X POST "http://localhost:8000/api/process/rerun-failed"
```

**Response**: `200 OK`
```json
{
  "success": true,
  "message": "Moved 3 failed PDFs back to newly_uploaded folder",
  "moved_count": 3
}
```

**Error Response**:
```json
{
  "success": false,
  "message": "No failed PDFs to rerun"
}
```

---

### 8. Download Failed PDFs

**Endpoint**: `GET /api/process/download-failed`

**Description**: Download all failed PDFs as a ZIP archive.

**Request**:
```bash
curl "http://localhost:8000/api/process/download-failed" \
  --output failed_pdfs.zip
```

**Response**: `200 OK`
- **Content-Type**: `application/zip`
- **Headers**: `Content-Disposition: attachment; filename=failed_pdfs_20241223_150000.zip`
- **Body**: ZIP file stream

**Error Responses**:
- `404`: No failed PDFs found

---

## Vision Processing Endpoints

### 9. Start Vision Processing

**Endpoint**: `POST /api/vision/start`

**Description**: Start vision model processing for registration fee table extraction from images.

**Request**:
```bash
curl -X POST "http://localhost:8000/api/vision/start"
```

**Response**: `200 OK`
```json
{
  "success": true,
  "message": "Started vision processing for registration fee extraction"
}
```

**Error Response**:
- `400`: Vision processing already running

**Notes**:
- Processes images in `data/left_over_reg_fee/` folder
- Uses YOLO for table detection + Gemini Vision for extraction
- Updates `PropertyDetail.registration_fee` in database

---

### 10. Stop Vision Processing

**Endpoint**: `POST /api/vision/stop`

**Description**: Stop ongoing vision processing.

**Request**:
```bash
curl -X POST "http://localhost:8000/api/vision/stop"
```

**Response**: `200 OK`
```json
{
  "success": true,
  "message": "Vision processing stopped. 2 image(s) remaining in left over reg fee folder.",
  "stopped_count": 2
}
```

---

### 11. Get Vision Statistics

**Endpoint**: `GET /api/vision/stats`

**Description**: Real-time vision processing statistics.

**Request**:
```bash
curl "http://localhost:8000/api/vision/stats"
```

**Response**: `200 OK`
```json
{
  "total": 10,
  "processed": 7,
  "successful": 6,
  "failed": 1,
  "is_running": true,
  "active_workers": 1,
  "current_file": "reg_fee_003.png"
}
```

---

## Data Retrieval Endpoints

### 12. Get All Documents

**Endpoint**: `GET /api/documents`

**Description**: Retrieve all processed documents with pagination.

**Query Parameters**:
- `skip` (int, optional): Offset for pagination. Default: 0
- `limit` (int, optional): Number of records per page. Default: 100

**Request**:
```bash
curl "http://localhost:8000/api/documents?skip=0&limit=10"
```

**Response**: `200 OK`
```json
[
  {
    "document_id": "DOC_2024_001",
    "batch_id": "BATCH_20241223_130000_a1b2c3d4",
    "transaction_date": "2024-01-15",
    "registration_office": "Sub-Registrar Office, Bangalore",
    "created_at": "2024-12-23T13:05:00",
    "updated_at": "2024-12-23T13:10:00",
    "property_details": {
      "id": 1,
      "document_id": "DOC_2024_001",
      "schedule_b_area": 1200.0,
      "schedule_c_property_name": "Residential Plot",
      "schedule_c_property_address": "123, MG Road, Bangalore",
      "schedule_c_property_area": 1200.0,
      "paid_in_cash_mode": "No",
      "pincode": "560001",
      "state": "Karnataka",
      "sale_consideration": 5000000.0,
      "stamp_duty_fee": 250000.0,
      "registration_fee": 50000.0,
      "guidance_value": 4800000.0
    },
    "buyers": [
      {
        "id": 1,
        "document_id": "DOC_2024_001",
        "name": "Rajesh Kumar",
        "gender": "Male",
        "aadhaar_number": "1234-5678-9012",
        "pan_card_number": "ABCDE1234F",
        "address": "456, Brigade Road, Bangalore",
        "pincode": "560025",
        "state": "Karnataka",
        "phone_number": "9876543210",
        "secondary_phone_number": "9876543211",
        "email": "rajesh@example.com"
      }
    ],
    "sellers": [
      {
        "id": 1,
        "document_id": "DOC_2024_001",
        "name": "Suresh Sharma",
        "gender": "Male",
        "aadhaar_number": "2345-6789-0123",
        "pan_card_number": "FGHIJ5678K",
        "address": "789, Residency Road, Bangalore",
        "pincode": "560025",
        "state": "Karnataka",
        "phone_number": "9876543220",
        "secondary_phone_number": null,
        "email": "suresh@example.com",
        "property_share": "100%"
      }
    ]
  }
]
```

---

### 13. Get Specific Document

**Endpoint**: `GET /api/documents/{document_id}`

**Description**: Retrieve a specific document by its ID.

**Path Parameters**:
- `document_id` (string, required): Unique document identifier

**Request**:
```bash
curl "http://localhost:8000/api/documents/DOC_2024_001"
```

**Response**: `200 OK`
- Same structure as single item in "Get All Documents"

**Error Response**:
- `404`: Document not found

---

### 14. Export to Excel

**Endpoint**: `GET /api/export/excel`

**Description**: Export processed data to Excel file with advanced filtering and formatting.

**Query Parameters**:
- `start_index` (int, optional): Starting record index. Default: 0
- `end_index` (int, optional): Ending record index. Default: all
- `batch_ids` (string, optional): Comma-separated batch IDs to filter. Example: `BATCH1,BATCH2`
- `batch_names` (string, optional): Comma-separated batch names for filename
- `start_date` (string, optional): Start date filter (ISO format)
- `end_date` (string, optional): End date filter (ISO format)
- `download_type` (string, optional): Download type (`all`, `batch`, `dateRange`)

**Request Examples**:

1. **Export All Data**:
```bash
curl "http://localhost:8000/api/export/excel?download_type=all" \
  --output whole_data.xlsx
```

2. **Export Specific Batches**:
```bash
curl "http://localhost:8000/api/export/excel?batch_ids=BATCH_20241223_130000_a1b2c3d4,BATCH_20241223_140000_e5f6g7h8&batch_names=Batch1,Batch2&download_type=batch" \
  --output multiple_batches_2.xlsx
```

3. **Export Date Range**:
```bash
curl "http://localhost:8000/api/export/excel?start_date=2024-01-01&end_date=2024-12-31&download_type=dateRange" \
  --output 2024-01-01_to_2024-12-31.xlsx
```

4. **Export with Pagination**:
```bash
curl "http://localhost:8000/api/export/excel?start_index=0&end_index=100" \
  --output first_100_records.xlsx
```

**Response**: `200 OK`
- **Content-Type**: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- **Headers**: `Content-Disposition: attachment; filename={dynamic_name}.xlsx`
- **Body**: Excel file stream

**Excel File Structure**:
- **Sheet Name**: `Sale_Deeds`
- **Headers**: Styled with blue background, white text, borders
- **Columns** (25 total):
  1. SL_NO
  2. USER_TYPE (S=Seller, B=Buyer)
  3. Document_ID
  4. Schedule_B_Area_sqft
  5. Schedule_C_Area_sqft
  6. Schedule_C_Address_Name
  7. Property_Pincode
  8. Property_State
  9. Sale_Consideration
  10. Stamp_Duty_Fee
  11. Registration_Fee
  12. Guidance_Value
  13. Cash_Payment
  14. Transaction_Date
  15. Registration_Office
  16. Name
  17. Gender
  18. Aadhaar
  19. PAN
  20. Address
  21. Pincode
  22. State
  23. Phone
  24. Secondary_Phone
  25. Email
  26. Property_Share (Seller only)

**Filename Patterns**:
- `whole_data.xlsx` - All data
- `{batch_name}.xlsx` - Single batch
- `multiple_batches_{count}.xlsx` - Multiple batches
- `{start_date}_to_{end_date}.xlsx` - Date range

**Excel Styling**:
- Header row: Bold, white text, blue background, centered
- Data rows: Borders, wrapped text, aligned left
- Column widths: Auto-sized for readability
- Row heights: 25px (header), 20px (data)

**Error Response**:
- `404`: No documents found for the selected criteria
- `500`: Export failed

---

## System Information Endpoints

### 15. Get System Health

**Endpoint**: `GET /api/system/info`

**Description**: System health check - CUDA, OCR tools, LLM connections, YOLO model status.

**Request**:
```bash
curl "http://localhost:8000/api/system/info"
```

**Response**: `200 OK`
```json
{
  "cuda_available": true,
  "cuda_device_count": 1,
  "poppler_available": true,
  "tesseract_available": true,
  "ollama_connected": true,
  "yolo_model_loaded": true
}
```

**Field Descriptions**:
- `cuda_available`: CUDA/GPU acceleration available
- `cuda_device_count`: Number of CUDA devices detected
- `poppler_available`: Poppler PDF tools installed (pdfinfo accessible)
- `tesseract_available`: Tesseract OCR installed
- `ollama_connected`: Ollama LLM server reachable
- `yolo_model_loaded`: YOLO ONNX model file exists

**Notes**:
- Poll this endpoint every 10 seconds for real-time health monitoring
- Used by frontend Footer component

---

### 16. Get System Configuration

**Endpoint**: `GET /api/system/config`

**Description**: Current pipeline and OCR configuration settings.

**Request**:
```bash
curl "http://localhost:8000/api/system/config"
```

**Response**: `200 OK`
```json
{
  "enable_pipeline": true,
  "max_ocr_workers": 2,
  "max_llm_workers": 8,
  "stage2_queue_size": 1,
  "enable_ocr_multiprocessing": true,
  "ocr_page_workers": 1,
  "max_workers": 2,
  "llm_backend": "gemini",
  "tesseract_lang": "eng+kan",
  "poppler_dpi": 300,
  "use_embedded_ocr": false
}
```

**Field Descriptions**:
- `enable_pipeline`: Pipeline Mode (V2) enabled
- `max_ocr_workers`: OCR worker count (Pipeline Mode)
- `max_llm_workers`: LLM worker count (Pipeline Mode)
- `stage2_queue_size`: Stage 2 queue size (Pipeline Mode)
- `enable_ocr_multiprocessing`: OCR multiprocessing enabled
- `ocr_page_workers`: Page-level OCR workers
- `max_workers`: Worker count (Legacy Mode)
- `llm_backend`: Active LLM backend (`gemini`, `ollama`, `groq`, etc.)
- `tesseract_lang`: Tesseract language data (`eng+kan`)
- `poppler_dpi`: PDF to image DPI (300)
- `use_embedded_ocr`: PyMuPDF embedded OCR mode

---

### 17. Get Folder Statistics

**Endpoint**: `GET /api/system/folders`

**Description**: File counts in processing folders.

**Request**:
```bash
curl "http://localhost:8000/api/system/folders"
```

**Response**: `200 OK`
```json
{
  "newly_uploaded": 5,
  "processed": 120,
  "failed": 3,
  "left_over_reg_fee": 8
}
```

**Field Descriptions**:
- `newly_uploaded`: PDFs waiting to be processed
- `processed`: Successfully processed PDFs
- `failed`: Failed PDFs
- `left_over_reg_fee`: Registration fee images for vision processing

---

## User Management Endpoints

### 18. Create User Info

**Endpoint**: `POST /api/user-info`

**Description**: Create user information entry before uploading files.

**Request Body** (JSON):
```json
{
  "user_name": "John Doe",
  "number_of_files": 10,
  "file_region": "Bangalore",
  "batch_id": null
}
```

**Parameters**:
- `user_name` (string, required): User's name
- `number_of_files` (int, required): Number of files to upload
- `file_region` (string, required): Region/location of files
- `batch_id` (string, optional): Batch ID (if already known)

**Request**:
```bash
curl -X POST "http://localhost:8000/api/user-info" \
  -H "Content-Type: application/json" \
  -d '{
    "user_name": "John Doe",
    "number_of_files": 10,
    "file_region": "Bangalore"
  }'
```

**Response**: `201 Created`
```json
{
  "id": 1,
  "user_name": "John Doe",
  "number_of_files": 10,
  "file_region": "Bangalore",
  "date": "2024-12-23T13:00:00",
  "batch_id": null,
  "created_at": "2024-12-23T13:00:00"
}
```

---

### 19. Get All User Info

**Endpoint**: `GET /api/user-info`

**Description**: Retrieve all user information entries (ordered by latest first).

**Request**:
```bash
curl "http://localhost:8000/api/user-info"
```

**Response**: `200 OK`
```json
[
  {
    "id": 2,
    "user_name": "Jane Smith",
    "number_of_files": 5,
    "file_region": "Mumbai",
    "date": "2024-12-23T14:00:00",
    "batch_id": "BATCH_20241223_140000_e5f6g7h8",
    "created_at": "2024-12-23T14:00:00"
  },
  {
    "id": 1,
    "user_name": "John Doe",
    "number_of_files": 10,
    "file_region": "Bangalore",
    "date": "2024-12-23T13:00:00",
    "batch_id": "BATCH_20241223_130000_a1b2c3d4",
    "created_at": "2024-12-23T13:00:00"
  }
]
```

---

### 20. Update User Info with Batch ID

**Endpoint**: `PATCH /api/user-info/update-batch`

**Description**: Link user info entry to batch ID after upload.

**Request Body** (JSON):
```json
{
  "user_name": "John Doe",
  "batch_id": "BATCH_20241223_130000_a1b2c3d4"
}
```

**Request**:
```bash
curl -X PATCH "http://localhost:8000/api/user-info/update-batch" \
  -H "Content-Type: application/json" \
  -d '{
    "user_name": "John Doe",
    "batch_id": "BATCH_20241223_130000_a1b2c3d4"
  }'
```

**Response**: `200 OK`
```json
{
  "success": true,
  "message": "User info updated with batch_id"
}
```

**Error Responses**:
- `400`: Missing user_name or batch_id
- `404`: User info entry not found

---

## Support Ticket Endpoints

### 21. Create Support Ticket

**Endpoint**: `POST /api/tickets`

**Description**: Create a new support ticket for error reporting.

**Request Body** (JSON):
```json
{
  "user_name": "John Doe",
  "batch_id": "BATCH_20241223_130000_a1b2c3d4",
  "error_type": "OCR Failure",
  "description": "OCR failed on 3 documents due to poor image quality"
}
```

**Parameters**:
- `user_name` (string, required): User's name
- `batch_id` (string, optional): Related batch ID
- `error_type` (string, required): Type of error
- `description` (string, required): Detailed error description

**Request**:
```bash
curl -X POST "http://localhost:8000/api/tickets" \
  -H "Content-Type: application/json" \
  -d '{
    "user_name": "John Doe",
    "batch_id": "BATCH_20241223_130000_a1b2c3d4",
    "error_type": "OCR Failure",
    "description": "OCR failed on 3 documents"
  }'
```

**Response**: `201 Created`
```json
{
  "id": 1,
  "user_name": "John Doe",
  "batch_id": "BATCH_20241223_130000_a1b2c3d4",
  "error_type": "OCR Failure",
  "description": "OCR failed on 3 documents due to poor image quality",
  "status": "open",
  "created_at": "2024-12-23T13:30:00",
  "resolved_at": null
}
```

---

### 22. Get All Tickets

**Endpoint**: `GET /api/tickets`

**Description**: Retrieve all support tickets (ordered by latest first).

**Request**:
```bash
curl "http://localhost:8000/api/tickets"
```

**Response**: `200 OK`
```json
[
  {
    "id": 2,
    "user_name": "Jane Smith",
    "batch_id": "BATCH_20241223_140000_e5f6g7h8",
    "error_type": "LLM Timeout",
    "description": "LLM extraction timed out after 5 minutes",
    "status": "in_progress",
    "created_at": "2024-12-23T14:30:00",
    "resolved_at": null
  },
  {
    "id": 1,
    "user_name": "John Doe",
    "batch_id": "BATCH_20241223_130000_a1b2c3d4",
    "error_type": "OCR Failure",
    "description": "OCR failed on 3 documents",
    "status": "resolved",
    "created_at": "2024-12-23T13:30:00",
    "resolved_at": "2024-12-23T15:00:00"
  }
]
```

**Ticket Status Values**:
- `open`: Newly created ticket
- `in_progress`: Being investigated
- `resolved`: Issue resolved
- `closed`: Ticket closed

---

### 23. Get Specific Ticket

**Endpoint**: `GET /api/tickets/{ticket_id}`

**Description**: Retrieve a specific ticket by ID.

**Path Parameters**:
- `ticket_id` (int, required): Ticket ID

**Request**:
```bash
curl "http://localhost:8000/api/tickets/1"
```

**Response**: `200 OK`
- Same structure as single item in "Get All Tickets"

**Error Response**:
- `404`: Ticket not found

---

### 24. Update Ticket Status

**Endpoint**: `PATCH /api/tickets/{ticket_id}/status`

**Description**: Update the status of a support ticket.

**Path Parameters**:
- `ticket_id` (int, required): Ticket ID

**Request Body** (JSON):
```json
{
  "status": "resolved"
}
```

**Valid Status Values**:
- `open`
- `in_progress`
- `resolved`
- `closed`

**Request**:
```bash
curl -X PATCH "http://localhost:8000/api/tickets/1/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "resolved"}'
```

**Response**: `200 OK`
```json
{
  "id": 1,
  "user_name": "John Doe",
  "batch_id": "BATCH_20241223_130000_a1b2c3d4",
  "error_type": "OCR Failure",
  "description": "OCR failed on 3 documents",
  "status": "resolved",
  "created_at": "2024-12-23T13:30:00",
  "resolved_at": "2024-12-23T15:00:00"
}
```

**Notes**:
- Setting status to `resolved` or `closed` automatically sets `resolved_at` timestamp
- `resolved_at` only set once (first time status changes to resolved/closed)

**Error Responses**:
- `400`: Invalid status value
- `404`: Ticket not found

---

## Error Handling

### Error Response Format
```json
{
  "detail": "Error message"
}
```

### Common HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid parameters or request body |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server error occurred |

### Error Examples

**Invalid Worker Count**:
```json
{
  "detail": "ocr_workers must be between 1 and 20"
}
```

**Processing Already Running**:
```json
{
  "detail": "Batch processing already running"
}
```

**Document Not Found**:
```json
{
  "detail": "Document not found"
}
```

---

## Rate Limiting

**Current Version**: No rate limiting (v1.0)

**Future Versions**: Will implement:
- Rate limiting per IP address
- Configurable rate limits
- Separate limits for different endpoint categories

**Recommended Client Behavior**:
- Poll `/process/stats` every 2 seconds (not faster)
- Poll `/system/info` every 10 seconds
- Respect server load indicators

---

## Best Practices

### 1. Polling for Progress
```javascript
// Poll processing stats every 2 seconds
const pollStats = setInterval(async () => {
  const response = await fetch('/api/process/stats');
  const stats = await response.json();

  if (!stats.is_running) {
    clearInterval(pollStats);
  }

  updateUI(stats);
}, 2000);
```

### 2. Error Handling
```javascript
try {
  const response = await fetch('/api/process/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ocr_workers: 2, llm_workers: 6 })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }

  const result = await response.json();
  console.log('Processing started:', result);
} catch (error) {
  console.error('Failed to start processing:', error.message);
}
```

### 3. File Upload
```javascript
const formData = new FormData();
files.forEach(file => formData.append('files', file));

const response = await fetch('/api/upload', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log('Batch ID:', result.batch_id);
```

### 4. Downloading Files
```javascript
// Download Excel
const response = await fetch('/api/export/excel?download_type=all');
const blob = await response.blob();
const url = window.URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'whole_data.xlsx';
a.click();
```

---

## API Summary Table

| Endpoint | Method | Category | Description |
|----------|--------|----------|-------------|
| `/api/upload` | POST | Upload | Upload PDF files |
| `/api/batches` | GET | Upload | Get all batches |
| `/api/process/start` | POST | Processing | Start PDF processing |
| `/api/process/stop` | POST | Processing | Stop PDF processing |
| `/api/process/stats` | GET | Processing | Get processing stats |
| `/api/process/toggle-embedded-ocr` | POST | Processing | Toggle OCR mode |
| `/api/process/rerun-failed` | POST | Processing | Rerun failed PDFs |
| `/api/process/download-failed` | GET | Processing | Download failed PDFs |
| `/api/vision/start` | POST | Vision | Start vision processing |
| `/api/vision/stop` | POST | Vision | Stop vision processing |
| `/api/vision/stats` | GET | Vision | Get vision stats |
| `/api/documents` | GET | Data | Get all documents |
| `/api/documents/{id}` | GET | Data | Get specific document |
| `/api/export/excel` | GET | Data | Export to Excel |
| `/api/system/info` | GET | System | Get system health |
| `/api/system/config` | GET | System | Get configuration |
| `/api/system/folders` | GET | System | Get folder stats |
| `/api/user-info` | POST | User | Create user info |
| `/api/user-info` | GET | User | Get all user info |
| `/api/user-info/update-batch` | PATCH | User | Update user batch |
| `/api/tickets` | POST | Tickets | Create ticket |
| `/api/tickets` | GET | Tickets | Get all tickets |
| `/api/tickets/{id}` | GET | Tickets | Get specific ticket |
| `/api/tickets/{id}/status` | PATCH | Tickets | Update ticket status |

**Total Endpoints**: 24

---

## Changelog

### Version 1.0 (December 2024)
- Initial API release
- 24 endpoints covering all core functionality
- Pipeline Mode (V2) support
- Batch tracking system
- User management
- Support ticket system
- Excel export with advanced filtering
- Vision processing for registration fees

---

## Support

For API questions or issues:
- Create a support ticket via `/api/tickets`
- Check GitHub issues: https://github.com/Nitinkaroshi/salesdeed/issues
- Review the main README: https://github.com/Nitinkaroshi/salesdeed

---

**Document Version**: 1.0
**API Version**: 1.0
**Last Updated**: December 23, 2024
