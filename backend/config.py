"""
ProduGen - Configuration Module
Loads environment variables and provides app-wide settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    # AI Service Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    REPLICATE_API_TOKEN: str = os.getenv("REPLICATE_API_TOKEN", "")

    # Server Settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # File Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_DIR: str = os.path.join(BASE_DIR, "uploads")
    OUTPUT_DIR: str = os.path.join(BASE_DIR, "outputs")
    DATA_DIR: str = os.path.join(BASE_DIR, "data")

    # Image Generation Settings
    MAX_IMAGES_FREE: int = 1
    MAX_IMAGES_STARTER: int = 3
    MAX_IMAGES_PRO: int = 5
    MAX_IMAGES_BUSINESS: int = 5

    # Supported Platform Dimensions (width x height)
    PLATFORM_SIZES: dict = {
        "instagram_post": (1080, 1080),
        "instagram_story": (1080, 1920),
        "facebook_post": (1200, 630),
        "website_banner": (1920, 1080),
        "square": (1024, 1024),
    }

    @classmethod
    def validate(cls) -> dict:
        """Check which API keys are configured."""
        status = {
            "gemini": bool(cls.GEMINI_API_KEY and cls.GEMINI_API_KEY != "your_gemini_api_key_here"),
            "replicate": bool(cls.REPLICATE_API_TOKEN and cls.REPLICATE_API_TOKEN != "your_replicate_api_token_here"),
        }
        return status

    @classmethod
    def ensure_directories(cls):
        """Create required directories if they don't exist."""
        for directory in [cls.UPLOAD_DIR, cls.OUTPUT_DIR, cls.DATA_DIR]:
            os.makedirs(directory, exist_ok=True)


# Create directories on import
Config.ensure_directories()
