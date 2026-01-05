# backend/app/config.py

import os
import sys
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Sale Deed Processor"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:admin@localhost:5432/sale_deed_db")

    # Paths - Handle both development and PyInstaller frozen modes
    @property
    def base_dir(self) -> Path:
        """Get base directory (handles PyInstaller frozen mode)"""
        if getattr(sys, 'frozen', False):
            # Running as compiled executable - use _MEIPASS (extracted files location)
            return Path(sys._MEIPASS)
        else:
            # Running in development mode
            return Path(__file__).resolve().parent.parent.parent

    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

    @property
    def data_dir(self) -> Path:
        """Data directory (always relative to executable location, not _internal)"""
        if getattr(sys, 'frozen', False):
            # In frozen mode, use parent of _internal for data directories
            exe_dir = Path(sys.executable).parent
            return exe_dir.parent / "data"
        return self.BASE_DIR / "data"

    DATA_DIR: Path = BASE_DIR / "data"
    NEWLY_UPLOADED_DIR: Path = DATA_DIR / "newly_uploaded"
    PROCESSED_DIR: Path = DATA_DIR / "processed"
    FAILED_DIR: Path = DATA_DIR / "failed"
    LEFT_OVER_REG_FEE_DIR: Path = DATA_DIR / "left_over_reg_fee"
    VISION_FAILED_DIR: Path = DATA_DIR / "vision_failed"

    @property
    def models_dir(self) -> Path:
        """Models directory (from bundle in frozen mode)"""
        return self.base_dir / "models"

    MODELS_DIR: Path = BASE_DIR / "models"

    @property
    def yolo_model_path(self) -> Path:
        """YOLO model path (from bundle in frozen mode)"""
        return self.models_dir / "table1.19.1.onnx"

    # YOLO Model
    YOLO_MODEL_PATH: Path = MODELS_DIR / "table1.19.1.onnx"
    YOLO_CONF_THRESHOLD: float = 0.86
    
    # Tesseract
    TESSERACT_LANG: str = "eng+kan"
    TESSERACT_OEM: int = 1
    TESSERACT_PSM: int = 4
    
    # Poppler - Use relative path from BASE_DIR (project root)
    POPPLER_PATH: Path = BASE_DIR.parent / "poppler" / "poppler-25.07.0" / "Library" / "bin"
    POPPLER_DPI: int = 300

    # Image Resolution Standardization
    # Images larger than this width will be resized to improve OCR performance
    # CRITICAL: Must resize to prevent memory overflow with Indic scripts
    # 2000px = ~242 DPI for A4 (good quality for Kannada while preventing OOM errors)
    TARGET_IMAGE_WIDTH: int = 2000  # Optimized for memory + quality balance
    
    # LLM Backend Configuration
    # Available backends: "ollama", "llamacpp", "vllm", "groq", "gemini"
    LLM_BACKEND: str = "gemini"  # Primary backend to use

    # Ollama Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_LLM_MODEL: str = "qwen2.5:3b-instruct"
    OLLAMA_VISION_MODEL: str = "qwen3-vl:4b"

    # llama.cpp Configuration
    USE_LLAMACPP: bool = False
    LLAMACPP_BASE_URL: str = "http://localhost:8080"
    LLAMACPP_LLM_MODEL: str = "qwen2.5-3b-instruct"
    LLAMACPP_VISION_MODEL: str = "qwen3-vl-4b"

    # vLLM Configuration (Production - High Performance)
    USE_VLLM: bool = False
    VLLM_BASE_URL: str = "http://localhost:8000"
    VLLM_LLM_MODEL: str = "Qwen/Qwen2.5-3B-Instruct"
    VLLM_VISION_MODEL: str = "Qwen/Qwen3-VL-4B"

    # Groq Configuration (Cloud API)
    USE_GROQ: bool = False
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = "meta-llama/llama-4-scout-17b-16e-instruct"

    # Gemini Configuration (Google Cloud API)
    USE_GEMINI: bool = True
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = "gemini-2.5-flash-lite"
    GEMINI_VISION_MODEL: str = "gemini-2.5-flash-lite"  # Gemini Flash Lite supports vision

    # LLM General Settings
    LLM_TEMPERATURE: float = 0.6
    LLM_MAX_TOKENS: int = 16384
    LLM_TIMEOUT: int = 300

    # Pipeline Processing (Version 2)
    ENABLE_PIPELINE: bool = True  # Enable pipeline parallelism
    MAX_OCR_WORKERS: int = 2      # REDUCED to 2 to prevent memory overflow (was 4)
    MAX_LLM_WORKERS: int = 8      # I/O-intensive workers (LLM API calls)
    STAGE2_QUEUE_SIZE: int = 1    # REDUCED to 1 to limit memory usage (was 2)

    # OCR Multiprocessing (Per-PDF page-level parallelism)
    ENABLE_OCR_MULTIPROCESSING: bool = True  # Enable multiprocessing for OCR pages
    OCR_PAGE_WORKERS: int = 1     # REDUCED to 1 to prevent memory overflow (was 2)

    # OCR Registration Fee Extraction (Backup extraction from OCR text)
    ENABLE_OCR_REG_FEE_EXTRACTION: bool = True  # Enable extraction of registration fee from OCR text (fallback when pdfplumber fails)

    # Embedded OCR Mode (PyMuPDF)
    USE_EMBEDDED_OCR: bool = False  # Enable PyMuPDF to read embedded OCR instead of Poppler+Tesseract

    # Legacy Processing (Version 1)
    MAX_WORKERS: int = 2          # Used only if ENABLE_PIPELINE = False
    BATCH_SIZE: int = 10
    
    # Validation
    MIN_REGISTRATION_FEE: float = 100.0
    MAX_MISC_FEE: float = 3000.0
    
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

# Override paths for PyInstaller frozen mode
if getattr(sys, 'frozen', False):
    # Update paths to use _MEIPASS (bundle directory)
    bundle_dir = Path(sys._MEIPASS)
    settings.MODELS_DIR = bundle_dir / "models"
    settings.YOLO_MODEL_PATH = settings.MODELS_DIR / "table1.19.1.onnx"

    # Data directories should be relative to executable, not bundle
    exe_dir = Path(sys.executable).parent
    settings.DATA_DIR = exe_dir.parent / "data"
    settings.NEWLY_UPLOADED_DIR = settings.DATA_DIR / "newly_uploaded"
    settings.PROCESSED_DIR = settings.DATA_DIR / "processed"
    settings.FAILED_DIR = settings.DATA_DIR / "failed"
    settings.LEFT_OVER_REG_FEE_DIR = settings.DATA_DIR / "left_over_reg_fee"
    settings.VISION_FAILED_DIR = settings.DATA_DIR / "vision_failed"

    print(f"[Frozen Mode] Models dir: {settings.MODELS_DIR}")
    print(f"[Frozen Mode] YOLO model: {settings.YOLO_MODEL_PATH}")
    print(f"[Frozen Mode] Data dir: {settings.DATA_DIR}")

settings.create_directories()
