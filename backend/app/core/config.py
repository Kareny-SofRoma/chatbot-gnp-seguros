from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # API Keys
    ANTHROPIC_API_KEY: str
    OPENAI_API_KEY: str
    PINECONE_API_KEY: str
    
    # Database
    DATABASE_URL: str
    REDIS_URL: str
    
    # Pinecone
    PINECONE_INDEX_NAME: str = "gnp-seguros"
    PINECONE_ENVIRONMENT: str = "us-east-1"
    
    # App
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "change-this-secret-key-in-production"
    
    # LLM
    LLM_MODEL: str = "claude-3-5-sonnet-20241022"
    TEMPERATURE: float = 0.2
    MAX_TOKENS: int = 2000
    
    # RAG
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K: int = 5
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    
    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
