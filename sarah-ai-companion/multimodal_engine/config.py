"""
Configuration settings for the Multimodal Engine service
"""

from pydantic_settings import BaseSettings
from typing import Optional
import torch


class Settings(BaseSettings):
    """Application settings"""
    
    # Service configuration
    SERVICE_NAME: str = "multimodal_engine"
    SERVICE_PORT: int = 8000
    
    # Model configuration
    FLUX_MODEL_PATH: str = "/app/models/black-forest-labs/FLUX.1-dev"
    DEVICE: str = "cuda" if torch.cuda.is_available() else "cpu"
    USE_FP16: bool = True
    
    # Generation defaults
    DEFAULT_INFERENCE_STEPS: int = 30
    DEFAULT_GUIDANCE_SCALE: float = 7.5
    DEFAULT_NEGATIVE_PROMPT: str = "bad anatomy, blurry, low quality, worst quality, low resolution, extra limbs, poorly drawn hands, missing limbs, ugly, duplicate, mutilated, mutated hands, poorly drawn face, deformed, bad proportions"
    
    # LoRA configuration
    LORA_OUTPUT_DIR: str = "/app/lora_models"
    MIN_LORA_IMAGES: int = 5
    MAX_LORA_IMAGES: int = 50
    
    # Output configuration
    OUTPUT_DIR: str = "/app/outputs"
    TEMP_DIR: str = "/app/temp"
    AUTO_CLEANUP: bool = True
    CLEANUP_DELAY: int = 3600  # 1 hour in seconds
    
    # ElevenLabs configuration
    ELEVENLABS_API_URL: str = "https://api.elevenlabs.io/v1"
    ELEVENLABS_API_KEY: str = ""
    DEFAULT_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice
    
    # External service URLs
    PERSONA_ENGINE_URL: str = "http://persona_engine:8000"
    
    # Memory limits
    MAX_IMAGE_SIZE: int = 2048
    MAX_BATCH_SIZE: int = 4
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
