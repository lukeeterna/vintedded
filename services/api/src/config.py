"""
Application configuration using Pydantic Settings.
All settings are loaded from environment variables.
"""
from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Application
    ENV: str = "development"
    DEBUG: bool = False
    VERSION: str = "2.0.0"
    APP_NAME: str = "Vinted Optimizer API"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/vinted"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "change-me-in-production-min-64-chars"
    ENCRYPTION_KEY: str = "change-me-in-production-fernet-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # CORS
    CORS_ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    
    @field_validator("CORS_ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    # Services
    AI_SERVICE_URL: str = "http://localhost:8001"
    SCRAPER_SERVICE_URL: str = "http://localhost:8002"
    
    # Shipping
    SENDCLOUD_API_KEY: str = ""
    SENDCLOUD_API_SECRET: str = ""
    
    # Observability
    SENTRY_DSN: str = ""
    OTEL_EXPORTER_OTLP_ENDPOINT: str = ""
    OTEL_SERVICE_NAME: str = "vinted-optimizer-api"
    LOG_LEVEL: str = "INFO"
    
    @property
    def is_production(self) -> bool:
        return self.ENV == "production"
    
    @property
    def is_development(self) -> bool:
        return self.ENV == "development"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()


settings = get_settings()
