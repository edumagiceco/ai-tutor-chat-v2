from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl


class Settings(BaseSettings):
    # Application
    PROJECT_NAME: str = "AI Tutor System"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # API
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str
    
    # AI Services
    ANTHROPIC_API_KEY: str
    OPENAI_API_KEY: str
    AI_SERVICE_URL: str
    
    # Qdrant
    QDRANT_URL: str
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()