"""
Configuration module for TUI client.
Loads settings from environment variables.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()


class Config:
    """Configuration settings for TUI client."""
    
    # API Configuration
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
    API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
    
    # Optional API Key (for future authentication)
    API_KEY = os.getenv("API_KEY", "")
    
    @classmethod
    def get_api_base_url(cls) -> str:
        """Get API base URL without trailing slash."""
        return cls.API_BASE_URL.rstrip("/")
    
    @classmethod
    def get_headers(cls) -> dict:
        """Get HTTP headers including API key if present."""
        headers = {}
        if cls.API_KEY:
            headers["Authorization"] = f"Bearer {cls.API_KEY}"
        return headers
