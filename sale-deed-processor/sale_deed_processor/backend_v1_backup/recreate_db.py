# backend/recreate_db.py

"""
Database recreation script
This will DROP all existing tables and recreate them with the new schema
WARNING: This will delete all existing data!
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent))

from app.database import engine
from app.models import Base
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Drop and recreate all database tables"""
    try:
        logger.info("="*60)
        logger.info("DATABASE RECREATION SCRIPT")
        logger.info("="*60)
        logger.info("This will DROP all existing tables and recreate them.")
        logger.info("All existing data will be LOST!")
        logger.info("="*60)

        # Drop all tables
        logger.info("Dropping all existing tables...")
        Base.metadata.drop_all(bind=engine)
        logger.info("✓ All tables dropped successfully")

        # Recreate all tables with new schema
        logger.info("Creating tables with updated schema...")
        Base.metadata.create_all(bind=engine)
        logger.info("✓ All tables created successfully with new schema")

        # Create directories
        logger.info("Creating directories...")
        settings.create_directories()
        logger.info("✓ Directories verified")

        logger.info("\n" + "="*60)
        logger.info("DATABASE RECREATION COMPLETE!")
        logger.info("="*60)
        logger.info("\nSchema changes applied:")
        logger.info("- sale_consideration: Float → String")
        logger.info("- stamp_duty_fee: Float → String")
        logger.info("- registration_fee: Float → String")
        logger.info("- guidance_value: Float → String")
        logger.info("\nYou can now restart your backend server and process PDFs.")
        logger.info("="*60)

    except Exception as e:
        logger.error(f"Database recreation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
