from pydantic import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "Attendance System"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # External Services
    ANTHROPIC_API_KEY: str
    META_API_KEY: Optional[str] = None

    # Database
    DATABASE_URL: str = "sqlite:///./attendance.db"

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    class Config:
        case_sensitive = True
        env_file = ".env-dev"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
