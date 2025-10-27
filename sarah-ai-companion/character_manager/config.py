"""
Configuration settings for the Character Manager service
"""

from pydantic_settings import BaseSettings
from typing import Optional, List, Dict


class Settings(BaseSettings):
    """Application settings"""
    
    # Service configuration
    SERVICE_NAME: str = "character_manager"
    SERVICE_PORT: int = 8000
    
    # Database configuration (shared with Memory Subsystem)
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "sarah_user"
    POSTGRES_PASSWORD: str = "sarah_password"
    POSTGRES_DB: str = "sarah_db"
    
    # External service URLs
    PERSONA_ENGINE_URL: str = "http://persona_engine:8000"
    MULTIMODAL_ENGINE_URL: str = "http://multimodal_engine:8000"
    
    # Character limits
    MAX_CHARACTERS_PER_USER: int = 50
    MIN_LORA_IMAGES: int = 5
    MAX_LORA_IMAGES: int = 50
    
    # Default values
    DEFAULT_VOICE_OPTIONS: List[Dict[str, str]] = [
        {
            "voice_id": "21m00Tcm4TlvDq8ikWAM",
            "name": "Rachel",
            "description": "Warm and friendly female voice"
        },
        {
            "voice_id": "AZnzlk1XvdvUeBnXmlld",
            "name": "Domi",
            "description": "Young and energetic female voice"
        },
        {
            "voice_id": "EXAVITQu4vr4xnSDxMaL",
            "name": "Bella",
            "description": "Soft and expressive female voice"
        }
    ]
    
    DEFAULT_PERSONALITY_TRAITS: List[str] = [
        "empathetic", "intelligent", "witty", "supportive", 
        "curious", "creative", "thoughtful", "playful"
    ]
    
    DEFAULT_HOBBIES: List[str] = [
        "reading", "music", "art", "cooking", "gaming",
        "hiking", "photography", "writing", "dancing"
    ]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False
    
    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL"""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
