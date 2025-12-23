# backend/app/services/vision_service_factory.py

import logging
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)


class BaseVisionService:
    """Base class for Vision services"""

    def extract_registration_fee(self, image_path: str) -> Optional[float]:
        """Extract registration fee from table image"""
        raise NotImplementedError("Subclass must implement extract_registration_fee")


class OllamaVisionService(BaseVisionService):
    """Ollama vision backend using existing implementation"""

    def __init__(self):
        from app.services.vision_service import VisionService
        self.service = VisionService(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_VISION_MODEL
        )
        logger.info(f"Initialized Ollama Vision: {settings.OLLAMA_VISION_MODEL}")

    def extract_registration_fee(self, image_path: str) -> Optional[float]:
        return self.service.extract_registration_fee(image_path)


class GeminiVisionService(BaseVisionService):
    """Google Gemini vision backend"""

    def __init__(self):
        from app.services.gemini_vision_service import GeminiVisionService as GeminiVisionImpl
        self.service = GeminiVisionImpl(
            api_key=settings.GEMINI_API_KEY,
            model=settings.GEMINI_VISION_MODEL
        )
        logger.info(f"Initialized Gemini Vision: {settings.GEMINI_VISION_MODEL}")

    def extract_registration_fee(self, image_path: str) -> Optional[float]:
        return self.service.extract_registration_fee(image_path)


def get_vision_service() -> BaseVisionService:
    """
    Factory function to get the appropriate vision service based on config

    Returns:
        BaseVisionService instance for the configured backend
    """
    backend = settings.LLM_BACKEND.lower()

    if backend == "gemini" and settings.USE_GEMINI:
        return GeminiVisionService()
    elif backend == "ollama":
        return OllamaVisionService()
    else:
        # Fallback to Gemini if configured, otherwise Ollama
        if settings.USE_GEMINI:
            logger.warning(f"Unknown backend '{backend}' for vision, falling back to Gemini")
            return GeminiVisionService()
        else:
            logger.warning(f"Unknown backend '{backend}' for vision, falling back to Ollama")
            return OllamaVisionService()
