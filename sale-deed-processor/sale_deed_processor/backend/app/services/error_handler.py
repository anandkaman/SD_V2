# backend/app/services/error_handler.py

"""
Error Handling & Recovery Service

Provides centralized error handling, classification, and recovery mechanisms.
"""

import logging
import traceback
from typing import Optional, Dict, Any, Callable
from functools import wraps
from datetime import datetime

logger = logging.getLogger(__name__)


class ErrorCategory:
    """Error categories for classification"""
    OCR_ERROR = "ocr_error"
    LLM_ERROR = "llm_error"
    DATABASE_ERROR = "database_error"
    VALIDATION_ERROR = "validation_error"
    FILE_ERROR = "file_error"
    NETWORK_ERROR = "network_error"
    UNKNOWN_ERROR = "unknown_error"


class ErrorHandler:
    """Centralized error handling service"""
    
    @staticmethod
    def classify_error(error: Exception) -> str:
        """
        Classify error into categories
        
        Args:
            error: Exception object
            
        Returns:
            Error category string
        """
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()
        
        # OCR errors
        if any(keyword in error_str for keyword in ['ocr', 'tesseract', 'image', 'pdf']):
            return ErrorCategory.OCR_ERROR
        
        # LLM errors
        if any(keyword in error_str for keyword in ['llm', 'openai', 'api', 'token', 'rate limit']):
            return ErrorCategory.LLM_ERROR
        
        # Database errors
        if any(keyword in error_type for keyword in ['sql', 'database', 'integrity', 'connection']):
            return ErrorCategory.DATABASE_ERROR
        
        # Validation errors
        if any(keyword in error_type for keyword in ['validation', 'pydantic', 'schema']):
            return ErrorCategory.VALIDATION_ERROR
        
        # File errors
        if any(keyword in error_type for keyword in ['file', 'io', 'permission']):
            return ErrorCategory.FILE_ERROR
        
        # Network errors
        if any(keyword in error_type for keyword in ['connection', 'timeout', 'network']):
            return ErrorCategory.NETWORK_ERROR
        
        return ErrorCategory.UNKNOWN_ERROR
    
    @staticmethod
    def get_user_friendly_message(error: Exception, category: str) -> str:
        """
        Get user-friendly error message
        
        Args:
            error: Exception object
            category: Error category
            
        Returns:
            User-friendly error message
        """
        messages = {
            ErrorCategory.OCR_ERROR: "Failed to extract text from PDF. The document may be corrupted or have poor image quality.",
            ErrorCategory.LLM_ERROR: "Failed to process document with AI. This may be due to API limits or service issues.",
            ErrorCategory.DATABASE_ERROR: "Database error occurred. Please try again or contact support.",
            ErrorCategory.VALIDATION_ERROR: "Invalid data provided. Please check your input and try again.",
            ErrorCategory.FILE_ERROR: "File operation failed. Please check file permissions and try again.",
            ErrorCategory.NETWORK_ERROR: "Network connection error. Please check your internet connection.",
            ErrorCategory.UNKNOWN_ERROR: "An unexpected error occurred. Please try again or contact support."
        }
        
        return messages.get(category, messages[ErrorCategory.UNKNOWN_ERROR])
    
    @staticmethod
    def is_retryable(category: str) -> bool:
        """
        Determine if error is retryable
        
        Args:
            category: Error category
            
        Returns:
            True if error can be retried
        """
        retryable_categories = [
            ErrorCategory.NETWORK_ERROR,
            ErrorCategory.LLM_ERROR,  # Rate limits, temporary API issues
            ErrorCategory.DATABASE_ERROR  # Temporary connection issues
        ]
        
        return category in retryable_categories
    
    @staticmethod
    def get_retry_strategy(category: str) -> Dict[str, Any]:
        """
        Get retry strategy for error category
        
        Args:
            category: Error category
            
        Returns:
            Dictionary with retry parameters
        """
        strategies = {
            ErrorCategory.NETWORK_ERROR: {
                "max_retries": 3,
                "delay_seconds": 5,
                "backoff_multiplier": 2
            },
            ErrorCategory.LLM_ERROR: {
                "max_retries": 5,
                "delay_seconds": 10,
                "backoff_multiplier": 2
            },
            ErrorCategory.DATABASE_ERROR: {
                "max_retries": 3,
                "delay_seconds": 2,
                "backoff_multiplier": 1.5
            }
        }
        
        return strategies.get(category, {
            "max_retries": 1,
            "delay_seconds": 5,
            "backoff_multiplier": 1
        })
    
    @staticmethod
    def log_error(
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        user_email: Optional[str] = None
    ):
        """
        Log error with context
        
        Args:
            error: Exception object
            context: Additional context information
            user_email: User who encountered the error
        """
        category = ErrorHandler.classify_error(error)
        
        log_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "error_category": category,
            "timestamp": datetime.utcnow().isoformat(),
            "user_email": user_email,
            "context": context,
            "traceback": traceback.format_exc()
        }
        
        logger.error(f"Error occurred: {log_data}")
        
        return log_data
    
    @staticmethod
    def handle_error(
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        user_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle error and return structured response
        
        Args:
            error: Exception object
            context: Additional context
            user_email: User who encountered error
            
        Returns:
            Dictionary with error details
        """
        category = ErrorHandler.classify_error(error)
        user_message = ErrorHandler.get_user_friendly_message(error, category)
        is_retryable = ErrorHandler.is_retryable(category)
        retry_strategy = ErrorHandler.get_retry_strategy(category) if is_retryable else None
        
        # Log error
        ErrorHandler.log_error(error, context, user_email)
        
        return {
            "success": False,
            "error_category": category,
            "error_message": user_message,
            "technical_details": str(error),
            "is_retryable": is_retryable,
            "retry_strategy": retry_strategy,
            "timestamp": datetime.utcnow().isoformat()
        }


def with_error_handling(func: Callable) -> Callable:
    """
    Decorator for automatic error handling
    
    Usage:
        @with_error_handling
        def my_function():
            # code that might fail
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_response = ErrorHandler.handle_error(e)
            logger.error(f"Error in {func.__name__}: {error_response}")
            raise
    
    return wrapper


def retry_on_error(max_retries: int = 3, delay: int = 5, backoff: float = 2):
    """
    Decorator for automatic retry on error
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay in seconds
        backoff: Backoff multiplier for each retry
        
    Usage:
        @retry_on_error(max_retries=3, delay=5, backoff=2)
        def my_function():
            # code that might fail
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    category = ErrorHandler.classify_error(e)
                    
                    if not ErrorHandler.is_retryable(category):
                        # Not retryable, raise immediately
                        raise
                    
                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}. "
                            f"Retrying in {current_delay}s... Error: {str(e)}"
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"All {max_retries} retry attempts failed for {func.__name__}"
                        )
                        raise
            
            # Should never reach here, but just in case
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator


# Global error handler instance
error_handler = ErrorHandler()
