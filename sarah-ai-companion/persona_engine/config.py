"""
Configuration settings for the Persona Engine service
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Service configuration
    SERVICE_NAME: str = "persona_engine"
    SERVICE_PORT: int = 8000
    
    # Ollama configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "mradermacher/DeepSeek-R1-Distill-Llama-8B-Abliterated-GGUF:Q4_K_M"
    OLLAMA_TIMEOUT: int = 300  # seconds
    
    # Redis configuration
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # External service URLs
    CHARACTER_MANAGER_URL: str = "http://character_manager:8000"
    MEMORY_SUBSYSTEM_URL: str = "http://memory_subsystem:8000"
    
    # Generation parameters
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_TOP_P: float = 0.9
    MAX_TOKENS: int = 2048
    
    # WebSocket configuration
    WS_PING_INTERVAL: int = 30  # seconds
    WS_PING_TIMEOUT: int = 10  # seconds
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
