# backend/app/utils/file_handler.py

import shutil
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class FileHandler:
    
    @staticmethod
    def extract_document_id(pdf_filename: str) -> str:
        """
        Extract document ID from PDF filename by removing _ocred.pdf suffix
        
        Args:
            pdf_filename: Name of PDF file
            
        Returns:
            Document ID (cleaned filename)
        """
        filename = Path(pdf_filename).stem
        
        # Remove _ocred suffix if present
        if filename.endswith('_ocred'):
            filename = filename[:-6]
        
        return filename
    
    @staticmethod
    def move_file(source: Path, destination_dir: Path, filename: str = None) -> Optional[Path]:
        """
        Move file to destination directory
        
        Args:
            source: Source file path
            destination_dir: Destination directory
            filename: Optional new filename
            
        Returns:
            New file path or None if failed
        """
        try:
            destination_dir.mkdir(parents=True, exist_ok=True)
            
            dest_filename = filename if filename else source.name
            dest_path = destination_dir / dest_filename
            
            shutil.move(str(source), str(dest_path))
            logger.info(f"Moved file: {source.name} -> {dest_path}")

            return dest_path
            
        except Exception as e:
            logger.error(f"Error moving file {source}: {e}")
            return None
    
    @staticmethod
    def get_pdf_files(directory: Path) -> list:
        """
        Get all PDF files from directory
        
        Args:
            directory: Directory path
            
        Returns:
            List of PDF file paths
        """
        if not directory.exists():
            logger.warning(f"Directory does not exist: {directory}")
            return []
        
        pdf_files = list(directory.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files in {directory}")
        
        return sorted(pdf_files)
    
    @staticmethod
    def save_table_image(image_array, output_path: Path) -> bool:
        """
        Save numpy array as image
        
        Args:
            image_array: Image array from OpenCV
            output_path: Output file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import cv2
            output_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(output_path), image_array)
            logger.info(f"Saved table image: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving image: {e}")
            return False