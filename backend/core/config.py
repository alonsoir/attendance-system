from functools import lru_cache
from typing import Optional

from pydantic import Field




class Settings:
    PROJECT_NAME: str = "Attendance System"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    project_description: str = "Sistema de gestión de ausencias escolares"


    # WhatsApp Settings
    WHATSAPP_CALLBACK_TOKEN: str = Field(
        default="default_callback_token",
        description="Token for WhatsApp webhook verification"
    )
    WHATSAPP_PROVIDER: str = Field(
        default="callmebot",
        description="WhatsApp message provider (callmebot, meta, mock)"
    )
    META_API_KEY: str = Field(
        default="",
        description="API Key for Meta/WhatsApp Business API"
    )

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
