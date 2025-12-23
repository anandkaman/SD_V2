# backend/app/api/routes.py

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import pandas as pd
import io
from pathlib import Path
import shutil
import logging
import zipfile
from datetime import datetime

from app.database import get_db
from app.schemas import (
    DocumentDetailSchema,
    ProcessingStatsSchema,
    SystemInfoSchema,
    BatchResultSchema
)

# Request models
class StartProcessingRequest(BaseModel):
    max_workers: int = 2
from app.models import DocumentDetail, PropertyDetail, BuyerDetail, SellerDetail
from app.services.pdf_processor import PDFProcessor
from app.workers.batch_processor import BatchProcessor
from app.workers.vision_batch_processor import VisionBatchProcessor
from app.utils.file_handler import FileHandler
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Global instances
batch_processor = BatchProcessor()
vision_batch_processor = VisionBatchProcessor()
pdf_processor = PDFProcessor(batch_processor=batch_processor)

# ==================== UPLOAD ENDPOINTS ====================

@router.post("/upload", response_model=dict)
async def upload_pdfs(files: List[UploadFile] = File(...)):
    """Upload PDF files to newly_uploaded folder"""
    try:
        uploaded_files = []
        
        for file in files:
            if not file.filename.endswith('.pdf'):
                continue
            
            file_path = settings.NEWLY_UPLOADED_DIR / file.filename
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            uploaded_files.append(file.filename)
            logger.info(f"Uploaded: {file.filename}")
        
        return {
            "success": True,
            "uploaded_count": len(uploaded_files),
            "files": uploaded_files
        }
    
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== PROCESSING ENDPOINTS ====================

@router.post("/process/start", response_model=dict)
async def start_batch_processing(background_tasks: BackgroundTasks, request: StartProcessingRequest = StartProcessingRequest()):
    """Start PDF OCR batch processing with configurable worker count"""
    try:
        max_workers = request.max_workers

        if batch_processor.is_running:
            raise HTTPException(status_code=400, detail="Batch processing already running")

        # Validate max_workers range (1-5)
        if max_workers < 1 or max_workers > 5:
            raise HTTPException(status_code=400, detail="max_workers must be between 1 and 5")

        pdf_files = FileHandler.get_pdf_files(settings.NEWLY_UPLOADED_DIR)

        if not pdf_files:
            return {
                "success": False,
                "message": "No PDF files found in newly_uploaded folder"
            }

        # Update batch processor max_workers
        batch_processor.max_workers = max_workers
        logger.info(f"Starting batch processing with {max_workers} workers")

        # Start processing in background
        background_tasks.add_task(
            batch_processor.process_batch,
            pdf_files,
            pdf_processor.process_single_pdf
        )

        return {
            "success": True,
            "message": f"Started processing {len(pdf_files)} PDFs with {max_workers} workers",
            "total_files": len(pdf_files),
            "max_workers": max_workers
        }

    except Exception as e:
        logger.error(f"Start processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process/stop", response_model=dict)
async def stop_batch_processing():
    """Stop PDF OCR batch processing (completes current tasks)"""
    try:
        if not batch_processor.is_running:
            return {
                "success": False,
                "message": "No batch processing is running"
            }

        batch_processor.stop()

        # Get stats to calculate how many might be stopped
        stats = batch_processor.get_stats()
        remaining = stats.get("total", 0) - stats.get("processed", 0)

        return {
            "success": True,
            "message": f"Processing stopped. {remaining} PDF(s) remaining in newly uploaded folder.",
            "stopped_count": remaining
        }

    except Exception as e:
        logger.error(f"Stop processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/process/stats", response_model=ProcessingStatsSchema)
async def get_processing_stats():
    """Get current processing statistics"""
    return batch_processor.get_stats()

@router.post("/process/rerun-failed", response_model=dict)
async def rerun_failed_pdfs():
    """Move all PDFs from failed folder back to newly_uploaded folder for reprocessing"""
    try:
        failed_dir = settings.FAILED_DIR
        newly_uploaded_dir = settings.NEWLY_UPLOADED_DIR

        failed_files = list(failed_dir.glob("*.pdf"))

        if not failed_files:
            return {
                "success": False,
                "message": "No failed PDFs to rerun"
            }

        moved_count = 0
        for pdf_file in failed_files:
            dest_path = newly_uploaded_dir / pdf_file.name
            shutil.move(str(pdf_file), str(dest_path))
            moved_count += 1
            logger.info(f"Moved {pdf_file.name} from failed to newly_uploaded")

        return {
            "success": True,
            "message": f"Moved {moved_count} failed PDFs back to newly_uploaded folder",
            "moved_count": moved_count
        }

    except Exception as e:
        logger.error(f"Rerun failed PDFs error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/process/download-failed")
async def download_failed_pdfs():
    """Download all failed PDFs as a ZIP file"""
    try:
        failed_dir = settings.FAILED_DIR
        failed_files = list(failed_dir.glob("*.pdf"))

        if not failed_files:
            raise HTTPException(status_code=404, detail="No failed PDFs found")

        # Create ZIP in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for pdf_file in failed_files:
                zip_file.write(pdf_file, pdf_file.name)
                logger.info(f"Added {pdf_file.name} to ZIP")

        zip_buffer.seek(0)

        filename = f"failed_pdfs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"

        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        logger.error(f"Download failed PDFs error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== VISION PROCESSING ENDPOINTS ====================

@router.post("/vision/start", response_model=dict)
async def start_vision_processing(background_tasks: BackgroundTasks):
    """Start vision model batch processing for registration fee tables"""
    try:
        if vision_batch_processor.is_running:
            raise HTTPException(status_code=400, detail="Vision processing already running")
        
        # Start processing in background
        background_tasks.add_task(vision_batch_processor.process_batch)
        
        return {
            "success": True,
            "message": "Started vision processing for registration fee extraction"
        }
    
    except Exception as e:
        logger.error(f"Start vision processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vision/stop", response_model=dict)
async def stop_vision_processing():
    """Stop vision batch processing"""
    try:
        if not vision_batch_processor.is_running:
            return {
                "success": False,
                "message": "No vision processing is running"
            }

        vision_batch_processor.stop()

        # Get stats
        stats = vision_batch_processor.get_stats()
        remaining = stats.get("total", 0) - stats.get("processed", 0)

        return {
            "success": True,
            "message": f"Vision processing stopped. {remaining} image(s) remaining in left over reg fee folder.",
            "stopped_count": remaining
        }

    except Exception as e:
        logger.error(f"Stop vision processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vision/stats", response_model=ProcessingStatsSchema)
async def get_vision_stats():
    """Get vision processing statistics"""
    return vision_batch_processor.get_stats()

# ==================== DATA RETRIEVAL ENDPOINTS ====================

@router.get("/documents", response_model=List[DocumentDetailSchema])
async def get_all_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all documents with pagination"""
    documents = db.query(DocumentDetail).offset(skip).limit(limit).all()
    return documents

@router.get("/documents/{document_id}", response_model=DocumentDetailSchema)
async def get_document(document_id: str, db: Session = Depends(get_db)):
    """Get specific document by ID"""
    document = db.query(DocumentDetail).filter(
        DocumentDetail.document_id == document_id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document

@router.get("/export/excel")
async def export_to_excel(
    start_index: int = 0,
    end_index: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Export data to Excel file"""
    try:
        query = db.query(DocumentDetail).offset(start_index)
        
        if end_index:
            query = query.limit(end_index - start_index)
        
        documents = query.all()
        
        # Prepare data for Excel
        rows = []
        for doc in documents:
            base_row = {
                "Document_ID": doc.document_id,
                "Transaction_Date": doc.transaction_date,
                "Registration_Office": doc.registration_office
            }
            
            # Add property details
            if doc.property_details:
                prop = doc.property_details
                base_row.update({
                    "Total_Land_Area_sqft": prop.total_land_area,
                    "Property_Address": prop.address,
                    "Property_Pincode": prop.pincode,
                    "Property_State": prop.state,
                    "Sale_Consideration": prop.sale_consideration,
                    "Stamp_Duty_Fee": prop.stamp_duty_fee,
                    "Registration_Fee": prop.registration_fee,
                    "Guidance_Value": prop.guidance_value
                })
            
            # Add buyers
            for idx, buyer in enumerate(doc.buyers, 1):
                row = base_row.copy()
                row.update({
                    "Person_Type": "Buyer",
                    "Person_Number": idx,
                    "Name": buyer.name,
                    "Gender": buyer.gender,
                    "Aadhaar": buyer.aadhaar_number,
                    "PAN": buyer.pan_card_number,
                    "Address": buyer.address,
                    "Pincode": buyer.pincode,
                    "State": buyer.state,
                    "Phone": buyer.phone_number,
                    "Secondary_Phone": buyer.secondary_phone_number,
                    "Email": buyer.email,
                    "Property_Share": None
                })
                rows.append(row)
            
            # Add sellers
            for idx, seller in enumerate(doc.sellers, 1):
                row = base_row.copy()
                row.update({
                    "Person_Type": "Seller",
                    "Person_Number": idx,
                    "Name": seller.name,
                    "Gender": seller.gender,
                    "Aadhaar": seller.aadhaar_number,
                    "PAN": seller.pan_card_number,
                    "Address": seller.address,
                    "Pincode": seller.pincode,
                    "State": seller.state,
                    "Phone": seller.phone_number,
                    "Secondary_Phone": seller.secondary_phone_number,
                    "Email": seller.email,
                    "Property_Share": seller.property_share
                })
                rows.append(row)
        
        df = pd.DataFrame(rows)
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sale_Deeds')
        
        output.seek(0)
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=sale_deeds_export.xlsx"}
        )
    
    except Exception as e:
        logger.error(f"Export error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== SYSTEM INFO ENDPOINTS ====================

@router.get("/system/info", response_model=SystemInfoSchema)
async def get_system_info():
    """Get system information and health status"""
    import torch
    import subprocess
    
    # Check CUDA
    cuda_available = torch.cuda.is_available()
    cuda_count = torch.cuda.device_count() if cuda_available else 0
    
    # Check Poppler
    try:
        subprocess.run(["pdfinfo", "-v"], capture_output=True, timeout=5)
        poppler_available = True
    except:
        poppler_available = False
    
    # Check Tesseract
    try:
        subprocess.run(["tesseract", "--version"], capture_output=True, timeout=5)
        tesseract_available = True
    except:
        tesseract_available = False
    
    # Check Ollama
    ollama_connected = pdf_processor.llm_service.check_connection()
    
    # Check YOLO model
    yolo_model_loaded = settings.YOLO_MODEL_PATH.exists()
    
    return {
        "cuda_available": cuda_available,
        "cuda_device_count": cuda_count,
        "poppler_available": poppler_available,
        "tesseract_available": tesseract_available,
        "ollama_connected": ollama_connected,
        "yolo_model_loaded": yolo_model_loaded
    }

@router.get("/system/folders", response_model=dict)
async def get_folder_stats():
    """Get file counts in each folder"""
    return {
        "newly_uploaded": len(list(settings.NEWLY_UPLOADED_DIR.glob("*.pdf"))),
        "processed": len(list(settings.PROCESSED_DIR.glob("*.pdf"))),
        "failed": len(list(settings.FAILED_DIR.glob("*.pdf"))),
        "left_over_reg_fee": len(list(settings.LEFT_OVER_REG_FEE_DIR.glob("*.png"))) + 
                             len(list(settings.LEFT_OVER_REG_FEE_DIR.glob("*.jpg")))
    }