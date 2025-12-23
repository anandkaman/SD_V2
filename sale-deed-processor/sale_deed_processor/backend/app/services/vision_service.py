# backend/app/services/vision_service.py

import requests
import json
import base64
from typing import Optional
from pathlib import Path
import logging
from app.config import settings
from app.utils.prompts import get_vision_registration_fee_prompt

logger = logging.getLogger(__name__)

class VisionService:
    def __init__(
        self,
        base_url: str = None,
        model: str = None
    ):
        """
        Initialize Vision service for Ollama

        Args:
            base_url: Ollama API base URL
            model: Vision model name
        """
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model = model or settings.OLLAMA_VISION_MODEL  # Updated to use new config
        self.api_url = f"{self.base_url}/api/generate"

        logger.info(f"Vision Service initialized: {self.model} at {self.base_url}")
    
    def encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def extract_registration_fee(self, image_path: str) -> Optional[float]:
        """
        Extract registration fee from table image using vision model
        
        Args:
            image_path: Path to cropped table image
            
        Returns:
            Registration fee as float or None if extraction failed
        """
        if not Path(image_path).exists():
            logger.error(f"Image not found: {image_path}")
            return None
        
        try:
            # Encode image
            image_base64 = self.encode_image(image_path)
            
            prompt = get_vision_registration_fee_prompt()

            payload = {
                "model": self.model,
                "prompt": prompt,
                "images": [image_base64],
                "stream": False,
                "format": "json"
            }
            
            logger.info(f"Sending image to vision model: {Path(image_path).name}")
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=400
            )
            
            if response.status_code != 200:
                logger.error(f"Vision API error: {response.status_code} - {response.text}")
                return None
            
            result = response.json()
            response_text = result.get("response", "")

            logger.info(f"Vision model raw response: {response_text}")

            # Parse JSON response
            try:
                data = json.loads(response_text)
                logger.info(f"Parsed JSON data: {data}")
                reg_fee = data.get("registration_fee")

                if reg_fee and isinstance(reg_fee, (int, float, str)):
                    try:
                        fee_value = float(reg_fee)
                        logger.info(f"Extracted registration fee from vision: {fee_value}")
                        return fee_value
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Cannot convert registration fee to float: {reg_fee} - {e}")
                        return None
                else:
                    logger.warning(f"Vision model returned null or invalid registration fee: {reg_fee} (type: {type(reg_fee)})")
                    return None

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse vision JSON response: {e}")
                logger.error(f"Response text was: {response_text}")
                return None
                
        except Exception as e:
            logger.error(f"Vision extraction error: {e}")
            return None