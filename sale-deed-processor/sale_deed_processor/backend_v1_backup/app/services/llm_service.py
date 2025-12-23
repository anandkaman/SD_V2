# backend/app/services/llm_service.py

from app.services.groq_llm_service import GroqLLMService #used when GROQ is enabled for testing only

import requests
import json
from typing import Dict, Optional
import logging
from app.config import settings
from app.utils.prompts import get_sale_deed_extraction_prompt

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(
        self,
        base_url: str = None,
        model: str = None,
        temperature: float = None
    ):
        """
        Initialize LLM service for Ollama
        
        Args:
            base_url: Ollama API base URL
            model: Model name
            temperature: Sampling temperature
        """
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model = model or settings.LLM_MODEL
        self.temperature = temperature or settings.LLM_TEMPERATURE
        self.api_url = f"{self.base_url}/api/generate"
        
        logger.info(f"LLM Service initialized: {self.model} at {self.base_url}")
    
    def check_connection(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info("Ollama connection successful")
                return True
            return False
        except Exception as e:
            logger.error(f"Cannot connect to Ollama: {e}")
            return False
    
    def extract_structured_data(self, ocr_text: str) -> Optional[Dict]:
        """
        Extract structured data from OCR text using LLM
        
        Args:
            ocr_text: Complete OCR text from document
            
        Returns:
            Extracted data as dictionary or None if failed
        """
        system_prompt = get_sale_deed_extraction_prompt()
        
        full_prompt = f"{system_prompt}\n\nHere is the OCR text from the sale deed document:\n\n{ocr_text}\n\nExtract the data and return ONLY valid JSON:"
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "temperature": self.temperature,
            "format": "json"
        }
        
        try:
            logger.info(f"Sending request to LLM (text length: {len(ocr_text)} chars)")
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=120
            )
            
            if response.status_code != 200:
                logger.error(f"LLM API error: {response.status_code} - {response.text}")
                return None
            
            result = response.json()
            response_text = result.get("response", "")
            
            # Parse JSON response
            try:
                extracted_data = json.loads(response_text)

                # Log what was extracted for debugging
                buyer_count = len(extracted_data.get("buyer_details", []))
                seller_count = len(extracted_data.get("seller_details", []))
                logger.info(f"Successfully extracted structured data from LLM: {buyer_count} buyers, {seller_count} sellers")

                # Log full response if no buyers/sellers found
                if buyer_count == 0 and seller_count == 0:
                    logger.warning(f"LLM returned ZERO buyers and sellers. Full response: {response_text[:1000]}")

                return extracted_data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM JSON response: {e}")
                logger.debug(f"Response text: {response_text[:500]}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("LLM request timeout")
            return None
        except Exception as e:
            logger.error(f"LLM extraction error: {e}")
            return None

def get_llm_service():
    """
    Dynamically choose between Groq API or local Ollama.
    """
    if settings.USE_GROQ:
        return GroqLLMService()

    return LLMService()
