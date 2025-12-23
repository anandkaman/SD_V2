# backend/init_db.py

"""
Database initialization script
Run this once to create all tables
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent))

from app.database import init_db
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Initialize database and create directories"""
    try:
        # Create directories
        logger.info("Creating directories...")
        settings.create_directories()
        logger.info("✓ Directories created")
        
        # Initialize database
        logger.info("Initializing database...")
        init_db()
        logger.info("✓ Database tables created successfully")
        
        # Verify YOLO model
        if settings.YOLO_MODEL_PATH.exists():
            logger.info(f"✓ YOLO model found: {settings.YOLO_MODEL_PATH}")
        else:
            logger.warning(f"⚠ YOLO model not found at: {settings.YOLO_MODEL_PATH}")
            logger.warning("  Please place table1.19.1.onnx in the models/ directory")
        
        logger.info("\n" + "="*50)
        logger.info("Initialization complete!")
        logger.info("="*50)
        logger.info("\nNext steps:")
        logger.info("1. Ensure Ollama is running with models:")
        logger.info(f"   - {settings.LLM_MODEL}")
        logger.info(f"   - {settings.VISION_MODEL}")
        logger.info("2. Place YOLO model in models/ directory")
        logger.info("3. Install Tesseract OCR and Poppler")
        logger.info("4. Start the API server:")
        logger.info("   uvicorn app.main:app --reload")
        
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()