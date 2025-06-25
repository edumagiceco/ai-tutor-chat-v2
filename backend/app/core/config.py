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
    
    # Celery
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    
    # AI Services
    ANTHROPIC_API_KEY: str
    OPENAI_API_KEY: str
    AI_SERVICE_URL: str
    
    # Qdrant
    QDRANT_URL: str
    QDRANT_HOST: Optional[str] = None
    QDRANT_PORT: Optional[int] = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Parse QDRANT_URL if host and port not provided
        if self.QDRANT_URL and not self.QDRANT_HOST:
            from urllib.parse import urlparse
            parsed = urlparse(self.QDRANT_URL)
            self.QDRANT_HOST = parsed.hostname or "qdrant"
            self.QDRANT_PORT = parsed.port or 6333
        
        # Set Celery URLs if not provided
        if not self.CELERY_BROKER_URL:
            self.CELERY_BROKER_URL = self.REDIS_URL + "/0"
        if not self.CELERY_RESULT_BACKEND:
            self.CELERY_RESULT_BACKEND = self.REDIS_URL + "/0"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


settings = Settings()