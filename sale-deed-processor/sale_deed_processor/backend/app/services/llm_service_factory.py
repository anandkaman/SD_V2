# backend/app/services/llm_service_factory.py

import logging
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)


class BaseLLMService:
    """Base class for LLM services"""

    def extract_structured_data(self, ocr_text: str) -> Optional[dict]:
        raise NotImplementedError("Subclass must implement extract_structured_data")

    def check_connection(self) -> bool:
        """Check if the LLM service is accessible"""
        raise NotImplementedError("Subclass must implement check_connection")


class OllamaLLMService(BaseLLMService):
    """Ollama backend using existing implementation"""

    def __init__(self):
        from app.services.llm_service import OllamaLLMService as OllamaImpl
        self.service = OllamaImpl(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_LLM_MODEL
        )
        logger.info(f"Initialized Ollama LLM: {settings.OLLAMA_LLM_MODEL}")

    def extract_structured_data(self, ocr_text: str) -> Optional[dict]:
        return self.service.extract_structured_data(ocr_text)

    def check_connection(self) -> bool:
        return self.service.check_connection()


class LlamaCppLLMService(BaseLLMService):
    """llama.cpp server backend (OpenAI-compatible API)"""

    def __init__(self):
        import requests
        self.base_url = settings.LLAMACPP_BASE_URL
        self.model = settings.LLAMACPP_LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.LLM_MAX_TOKENS
        self.timeout = settings.LLM_TIMEOUT
        logger.info(f"Initialized llama.cpp LLM: {self.model} at {self.base_url}")

    def extract_structured_data(self, ocr_text: str) -> Optional[dict]:
        import requests
        import json
        from app.utils.prompts import get_sale_deed_extraction_prompt

        try:
            system_prompt = get_sale_deed_extraction_prompt()

            # llama.cpp uses OpenAI-compatible API
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": ocr_text}
                    ],
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                    "response_format": {"type": "json_object"}
                },
                timeout=self.timeout
            )

            if response.status_code != 200:
                logger.error(f"llama.cpp API error: {response.status_code}")
                return None

            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

            return json.loads(content)

        except Exception as e:
            logger.error(f"llama.cpp extraction error: {e}")
            return None

    def check_connection(self) -> bool:
        """Check if llama.cpp server is accessible"""
        try:
            import requests
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"llama.cpp connection check failed: {e}")
            return False


class VLLMLLMService(BaseLLMService):
    """vLLM backend (OpenAI-compatible API) - Production optimized"""

    def __init__(self):
        import requests
        self.base_url = settings.VLLM_BASE_URL
        self.model = settings.VLLM_LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.LLM_MAX_TOKENS
        self.timeout = settings.LLM_TIMEOUT
        logger.info(f"Initialized vLLM LLM: {self.model} at {self.base_url}")

    def extract_structured_data(self, ocr_text: str) -> Optional[dict]:
        import requests
        import json
        from app.utils.prompts import get_sale_deed_extraction_prompt

        try:
            system_prompt = get_sale_deed_extraction_prompt()

            # vLLM uses OpenAI-compatible API
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": ocr_text}
                    ],
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                    "response_format": {"type": "json_object"}
                },
                timeout=self.timeout
            )

            if response.status_code != 200:
                logger.error(f"vLLM API error: {response.status_code}")
                return None

            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

            return json.loads(content)

        except Exception as e:
            logger.error(f"vLLM extraction error: {e}")
            return None

    def check_connection(self) -> bool:
        """Check if vLLM server is accessible"""
        try:
            import requests
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"vLLM connection check failed: {e}")
            return False


class GroqLLMService(BaseLLMService):
    """Groq Cloud API backend (existing implementation)"""

    def __init__(self):
        from app.services.llm_service import GroqLLMService as GroqImpl
        self.service = GroqImpl(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL
        )
        logger.info(f"Initialized Groq LLM: {settings.GROQ_MODEL}")

    def extract_structured_data(self, ocr_text: str) -> Optional[dict]:
        return self.service.extract_structured_data(ocr_text)

    def check_connection(self) -> bool:
        return self.service.check_connection()


class GeminiLLMService(BaseLLMService):
    """Google Gemini Cloud API backend"""

    def __init__(self):
        from app.services.gemini_llm_service import GeminiLLMService as GeminiImpl
        self.service = GeminiImpl(
            api_key=settings.GEMINI_API_KEY,
            model=settings.GEMINI_MODEL
        )
        logger.info(f"Initialized Gemini LLM: {settings.GEMINI_MODEL}")

    def extract_structured_data(self, ocr_text: str) -> Optional[dict]:
        return self.service.extract_structured_data(ocr_text)

    def check_connection(self) -> bool:
        return self.service.check_connection()


def get_llm_service() -> BaseLLMService:
    """
    Factory function to get the appropriate LLM service based on config

    Returns:
        BaseLLMService instance for the configured backend
    """
    backend = settings.LLM_BACKEND.lower()

    if backend == "gemini" and settings.USE_GEMINI:
        return GeminiLLMService()
    elif backend == "groq" and settings.USE_GROQ:
        return GroqLLMService()
    elif backend == "vllm" and settings.USE_VLLM:
        return VLLMLLMService()
    elif backend == "llamacpp" and settings.USE_LLAMACPP:
        return LlamaCppLLMService()
    elif backend == "ollama":
        return OllamaLLMService()
    else:
        # Fallback to Gemini if configured, otherwise Groq if configured, otherwise Ollama
        if settings.USE_GEMINI:
            logger.warning(f"Unknown backend '{backend}', falling back to Gemini")
            return GeminiLLMService()
        elif settings.USE_GROQ:
            logger.warning(f"Unknown backend '{backend}', falling back to Groq")
            return GroqLLMService()
        else:
            logger.warning(f"Unknown backend '{backend}', falling back to Ollama")
            return OllamaLLMService()
