import json
import logging
from typing import Dict, Optional
from groq import Groq, APIError, APIConnectionError
from ..config import settings
from ..utils.prompts import get_sale_deed_extraction_prompt

logger = logging.getLogger(__name__)

class GroqLLMService:
    def __init__(self, api_key: str = None, model: str = None):
        """
        Groq API-based LLM service
        """
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = model or settings.GROQ_MODEL
        self.client = Groq(api_key=self.api_key)

        logger.info(f"Groq LLM initialized with model: {self.model}")

    def extract_structured_data(self, ocr_text: str) -> Optional[Dict]:
        """
        Extract structured JSON using Groq chat completion API
        """

        system_prompt = get_sale_deed_extraction_prompt()
        user_prompt = f"Here is the complete OCR text from the document:\n\n{ocr_text}"

        try:
            logger.info(f"Sending {len(ocr_text)} chars to Groq model {self.model}")

            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                model=self.model,
                temperature=0,
                response_format={"type": "json_object"}
            )

            response_text = chat_completion.choices[0].message.content

            data = json.loads(response_text)

            logger.info(f"Groq successfully returned structured JSON")

            return data

        except APIConnectionError as e:
            logger.error(f"Groq Connection Error: {e}")
            return None

        except APIError as e:
            logger.error(f"Groq API Error: {e}")
            return None

        except json.JSONDecodeError as e:
            logger.error(f"Groq returned non-JSON: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected Groq error: {e}")
            return None

    def check_connection(self) -> bool:
        """
        Check if Groq API is accessible
        """
        try:
            # Make a minimal API call to check connection
            self.client.chat.completions.create(
                messages=[{"role": "user", "content": "test"}],
                model=self.model,
                max_tokens=1
            )
            return True
        except Exception as e:
            logger.warning(f"Groq connection check failed: {e}")
            return False
