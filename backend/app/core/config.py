from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    APP_NAME: str = "ML Deployment Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    HOST: str = "127.0.0.1"
    PORT: int = 9000
    
    DATABASE_URL: str = "sqlite+aiosqlite:///./mlplatform.db"
    DATABASE_URL_SYNC: str = "sqlite:///./mlplatform.db"
    
    SECRET_KEY: str = "your-super-secret-key-change-in-production-min-32-chars-long"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    REDIS_URL: str = "redis://localhost:6379/0"
    
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    UPLOAD_DIR: str = "models"
    MAX_UPLOAD_SIZE: int = 104857600
    
    RATE_LIMIT_PER_MINUTE: int = 60

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
