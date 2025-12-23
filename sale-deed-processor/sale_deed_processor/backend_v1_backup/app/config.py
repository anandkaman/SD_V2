# backend/app/config.py

import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Sale Deed Processor"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:admin@localhost:5432/sale_deed_db"
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    NEWLY_UPLOADED_DIR: Path = DATA_DIR / "newly_uploaded"
    PROCESSED_DIR: Path = DATA_DIR / "processed"
    FAILED_DIR: Path = DATA_DIR / "failed"
    LEFT_OVER_REG_FEE_DIR: Path = DATA_DIR / "left_over_reg_fee"
    VISION_FAILED_DIR: Path = DATA_DIR / "vision_failed"
    MODELS_DIR: Path = BASE_DIR / "models"
    
    # YOLO Model
    YOLO_MODEL_PATH: Path = MODELS_DIR / "table1.19.1.onnx"
    YOLO_CONF_THRESHOLD: float = 0.65
    
    # Tesseract
    TESSERACT_LANG: str = "eng+kan"
    TESSERACT_OEM: int = 1
    TESSERACT_PSM: int = 4
    
    # Poppler
    POPPLER_PATH: str = r"C:\Program Files\poppler\Library\bin"  # Update for your system
    POPPLER_DPI: int = 300
    
    # LLM
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "qwen2.5:3b-instruct"
    VISION_MODEL: str = "qwen3-vl:4b"
    LLM_TEMPERATURE: float = 0.6

    # Groq LLM
    USE_GROQ: bool = True                    # Switch here
    GROQ_API_KEY: str = ""  # Add your Groq API key here or set via environment variable
    GROQ_MODEL: str = "meta-llama/llama-4-scout-17b-16e-instruct" 
    
    # Processing
    MAX_WORKERS: int = 2
    BATCH_SIZE: int = 10
    
    # Validation
    MIN_REGISTRATION_FEE: float = 4000.0
    MAX_MISC_FEE: float = 4000.0
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    def create_directories(self):
        """Create necessary directories if they don't exist"""
        for dir_path in [
            self.DATA_DIR,
            self.NEWLY_UPLOADED_DIR,
            self.PROCESSED_DIR,
            self.FAILED_DIR,
            self.LEFT_OVER_REG_FEE_DIR,
            self.VISION_FAILED_DIR,
            self.MODELS_DIR
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)

settings = Settings()
settings.create_directories()