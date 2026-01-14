import json
import logging
from typing import Dict, Optional
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from ..config import settings
from ..utils.prompts import get_sale_deed_extraction_prompt

logger = logging.getLogger(__name__)

class GeminiLLMService:
    def __init__(self, api_key: str = None, model: str = None):
        """
        Google Gemini API-based LLM service

        Args:
            api_key: Gemini API key (defaults to settings.GEMINI_API_KEY)
            model: Model name (defaults to settings.GEMINI_MODEL)
        """
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model or settings.GEMINI_MODEL

        # Configure the Gemini API
        genai.configure(api_key=self.api_key)

        # Initialize the model with JSON response configuration
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={
                "temperature": settings.LLM_TEMPERATURE,
                "max_output_tokens": settings.LLM_MAX_TOKENS,
                "response_mime_type": "application/json"
            }
        )

        logger.info(f"Gemini LLM initialized with model: {self.model_name}")

    def extract_structured_data(self, ocr_text: str, images: list = None) -> Optional[Dict]:
        """
        Extract structured JSON using Gemini API
        
        Args:
            ocr_text: OCR text from the document
            images: Optional list of PIL Image objects (first few pages for better accuracy)
        
        Returns:
            Extracted data as dictionary or None if failed
        """
        system_prompt = get_sale_deed_extraction_prompt()
        
        try:
            if images and len(images) > 0:
                # Vision + OCR mode: Send images with OCR text
                logger.info(f"Sending {len(images)} images + {len(ocr_text)} chars OCR to Gemini model {self.model_name}")
                
                # Build content list: [prompt, image1, image2, ..., ocr_text]
                content = [system_prompt]
                content.extend(images)
                content.append(f"\n\nHere is the complete OCR text from the document:\n\n{ocr_text}\n\nExtract the data and return ONLY valid JSON:")
                
                response = self.model.generate_content(content)
            else:
                # OCR-only mode (fallback)
                logger.info(f"Sending {len(ocr_text)} chars to Gemini model {self.model_name} (OCR only)")
                full_prompt = f"{system_prompt}\n\nHere is the complete OCR text from the document:\n\n{ocr_text}\n\nExtract the data and return ONLY valid JSON:"
                response = self.model.generate_content(full_prompt)

            # Get the response text
            response_text = response.text

            # Parse JSON response
            data = json.loads(response_text)

            logger.info(f"Gemini successfully returned structured JSON")

            # Log extraction details
            buyer_count = len(data.get("buyer_details", []))
            seller_count = len(data.get("seller_details", []))
            logger.info(f"Extracted {buyer_count} buyers, {seller_count} sellers")

            return data

        except google_exceptions.GoogleAPIError as e:
            logger.error(f"Gemini API Error: {e}")
            return None

        except json.JSONDecodeError as e:
            logger.error(f"Gemini returned non-JSON: {e}")
            logger.debug(f"Response text: {response_text[:500] if 'response_text' in locals() else 'N/A'}")
            return None

        except Exception as e:
            logger.error(f"Unexpected Gemini error: {e}")
            return None

    def check_connection(self) -> bool:
        """
        Check if Gemini API is accessible

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Make a minimal API call to check connection
            test_model = genai.GenerativeModel(model_name=self.model_name)
            response = test_model.generate_content("test")

            logger.info("Gemini connection successful")
            return True

        except Exception as e:
            logger.warning(f"Gemini connection check failed: {e}")
            return False
