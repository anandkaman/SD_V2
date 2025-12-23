# backend/app/exceptions.py

class ProcessingStoppedException(Exception):
    """Exception raised when user stops batch processing"""

    def __init__(self, message: str = "Processing stopped by user"):
        self.message = message
        super().__init__(self.message)
