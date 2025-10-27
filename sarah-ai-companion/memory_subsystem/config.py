"""
Configuration settings for the Memory Subsystem service
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Service configuration
    SERVICE_NAME: str = "memory_subsystem"
    SERVICE_PORT: int = 8000
    
    # PostgreSQL configuration
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "sarah_user"
    POSTGRES_PASSWORD: str = "sarah_password"
    POSTGRES_DB: str = "sarah_db"
    
    # Milvus configuration
    MILVUS_HOST: str = "milvus"
    MILVUS_PORT: int = 19530
    
    # Redis configuration
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Sentence transformer model
    SENTENCE_MODEL_PATH: str = "/app/models/sentence-transformer"
    EMBEDDING_DIM: int = 384  # all-MiniLM-L6-v2 dimension
    
    # External service URLs
    PERSONA_ENGINE_URL: str = "http://persona_engine:8000"
    
    # Memory settings
    MAX_FACTS_PER_USER: int = 10000
    MAX_CONVERSATIONS_PER_USER: int = 50000
    CONVERSATION_CHUNK_SIZE: int = 500  # Characters per chunk
    
    # Performance settings
    BATCH_SIZE: int = 100
    WORKER_CONCURRENCY: int = 4
    
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
