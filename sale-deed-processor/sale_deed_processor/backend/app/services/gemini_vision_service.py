import json
import logging
from typing import Optional
from pathlib import Path
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from PIL import Image
from ..config import settings
from ..utils.prompts import get_vision_registration_fee_prompt

logger = logging.getLogger(__name__)

class GeminiVisionService:
    def __init__(self, api_key: str = None, model: str = None):
        """
        Google Gemini Vision API service

        Args:
            api_key: Gemini API key (defaults to settings.GEMINI_API_KEY)
            model: Vision model name (defaults to settings.GEMINI_VISION_MODEL)
        """
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model or settings.GEMINI_VISION_MODEL

        # Configure the Gemini API
        genai.configure(api_key=self.api_key)

        # Initialize the model with JSON response configuration
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={
                "temperature": 0,  # Use 0 for vision extraction tasks
                "max_output_tokens": settings.LLM_MAX_TOKENS,
                "response_mime_type": "application/json"
            }
        )

        logger.info(f"Gemini Vision Service initialized: {self.model_name}")

    def extract_registration_fee(self, image_path: str) -> Optional[float]:
        """
        Extract registration fee from table image using Gemini vision model

        Args:
            image_path: Path to cropped table image

        Returns:
            Registration fee as float or None if extraction failed
        """
        if not Path(image_path).exists():
            logger.error(f"Image not found: {image_path}")
            return None

        try:
            # Load the image using PIL
            image = Image.open(image_path)

            # Get the prompt
            prompt = get_vision_registration_fee_prompt()

            logger.info(f"Sending image to Gemini vision model: {Path(image_path).name}")

            # Generate content with image and prompt
            response = self.model.generate_content([prompt, image])

            # Get the response text
            response_text = response.text

            logger.info(f"Gemini vision model raw response: {response_text}")

            # Parse JSON response
            try:
                data = json.loads(response_text)
                logger.info(f"Parsed JSON data: {data}")
                reg_fee = data.get("registration_fee")

                if reg_fee and isinstance(reg_fee, (int, float, str)):
                    try:
                        fee_value = float(reg_fee)
                        logger.info(f"Extracted registration fee from Gemini vision: {fee_value}")
                        return fee_value
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Cannot convert registration fee to float: {reg_fee} - {e}")
                        return None
                else:
                    logger.warning(f"Gemini vision returned null or invalid registration fee: {reg_fee} (type: {type(reg_fee)})")
                    return None

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini vision JSON response: {e}")
                logger.error(f"Response text was: {response_text}")
                return None

        except google_exceptions.GoogleAPIError as e:
            logger.error(f"Gemini Vision API Error: {e}")
            return None

        except Exception as e:
            logger.error(f"Gemini vision extraction error: {e}")
            return None
