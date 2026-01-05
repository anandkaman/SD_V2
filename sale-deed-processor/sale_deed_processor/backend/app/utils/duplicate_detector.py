# backend/app/utils/duplicate_detector.py

"""
Duplicate Detection Utility

Provides functionality to detect duplicate PDF uploads based on file content hash.
"""

import hashlib
from pathlib import Path
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from app.models import DocumentDetail
import logging

logger = logging.getLogger(__name__)


def calculate_file_hash(file_path: Path) -> str:
    """
    Calculate SHA256 hash of a file
    
    Args:
        file_path: Path to the file
        
    Returns:
        Hexadecimal string of SHA256 hash
    """
    sha256_hash = hashlib.sha256()
    
    with open(file_path, "rb") as f:
        # Read file in chunks to handle large files
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    return sha256_hash.hexdigest()


def check_duplicate(file_hash: str, db: Session) -> Optional[Dict]:
    """
    Check if a file with the same hash already exists in database
    
    Args:
        file_hash: SHA256 hash of the file
        db: Database session
        
    Returns:
        Dictionary with duplicate info if found, None otherwise
        {
            "is_duplicate": True,
            "document_id": "...",
            "batch_id": "...",
            "created_at": "...",
            "transaction_date": "..."
        }
    """
    existing_doc = db.query(DocumentDetail).filter(
        DocumentDetail.file_hash == file_hash
    ).first()
    
    if existing_doc:
        return {
            "is_duplicate": True,
            "document_id": existing_doc.document_id,
            "batch_id": existing_doc.batch_id,
            "created_at": existing_doc.created_at.isoformat() if existing_doc.created_at else None,
            "transaction_date": existing_doc.transaction_date.isoformat() if existing_doc.transaction_date else None
        }
    
    return None


def check_batch_duplicates(file_paths: List[Path], db: Session) -> Dict:
    """
    Check multiple files for duplicates
    
    Args:
        file_paths: List of file paths to check
        db: Database session
        
    Returns:
        Dictionary with duplicate information
        {
            "total_files": 10,
            "duplicates_found": 2,
            "duplicate_details": [
                {
                    "filename": "file1.pdf",
                    "hash": "abc123...",
                    "existing_document": {...}
                }
            ],
            "unique_files": 8
        }
    """
    duplicates = []
    unique_count = 0
    
    for file_path in file_paths:
        try:
            file_hash = calculate_file_hash(file_path)
            duplicate_info = check_duplicate(file_hash, db)
            
            if duplicate_info:
                duplicates.append({
                    "filename": file_path.name,
                    "hash": file_hash,
                    "existing_document": duplicate_info
                })
                logger.warning(f"Duplicate detected: {file_path.name} matches {duplicate_info['document_id']}")
            else:
                unique_count += 1
                
        except Exception as e:
            logger.error(f"Error checking duplicate for {file_path.name}: {e}")
    
    return {
        "total_files": len(file_paths),
        "duplicates_found": len(duplicates),
        "duplicate_details": duplicates,
        "unique_files": unique_count
    }


def save_file_hash(document_id: str, file_hash: str, db: Session) -> bool:
    """
    Save or update file hash for a document
    
    Args:
        document_id: Document ID
        file_hash: SHA256 hash of the file
        db: Database session
        
    Returns:
        True if successful, False otherwise
    """
    try:
        doc = db.query(DocumentDetail).filter(
            DocumentDetail.document_id == document_id
        ).first()
        
        if doc:
            doc.file_hash = file_hash
            db.commit()
            logger.info(f"Saved file hash for {document_id}")
            return True
        else:
            logger.warning(f"Document {document_id} not found for hash update")
            return False
            
    except Exception as e:
        logger.error(f"Error saving file hash for {document_id}: {e}")
        db.rollback()
        return False
