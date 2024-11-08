import logging
import sys
from typing import Any, Dict, List, Optional
from pydantic import BaseSettings, PostgresDsn, validator
from pydantic_settings import BaseSettings


class LogConfig:
    """Configuración de logging"""
    LOGGER_NAME: str = "attendance_system"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = "DEBUG"

    # Configuración de loggers por defecto
    version = 1
    disable_existing_loggers = False
    formatters = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "file": {
            "formatter": "default",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "attendance_system.log",
            "maxBytes": 10000000,  # 10MB
            "backupCount": 5,
        },
    }
    loggers = {
        LOGGER_NAME: {"handlers": ["default", "file"], "level": LOG_LEVEL},
    }


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Attendance System"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "Sistema de gestión de ausencias escolares"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:5173",  # Vite default
    ]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URI: Optional[PostgresDsn] = None

    @validator("DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    # JWT
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # External Services
    ANTHROPIC_API_KEY: str
    META_API_KEY: Optional[str] = None
    WHATSAPP_CALLBACK_TOKEN: Optional[str] = None

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Cache
    REDIS_URL: Optional[str] = None
    CACHE_TTL_SECONDS: int = 3600  # 1 hour

    # Monitoring
    SENTRY_DSN: Optional[str] = None
    ENABLE_METRICS: bool = True

    # Internacionalización
    DEFAULT_LANGUAGE: str = "es-ES"
    SUPPORTED_LANGUAGES: List[str] = ["en-US", "es-ES"]

    class Config:
        case_sensitive = True
        env_file = ".env-dev"
        env_file_encoding = "utf-8"

    def get_supported_languages(self) -> List[Dict[str, str]]:
        return [
            {"code": "en-US", "name": "English (US)"},
            {"code": "es-ES", "name": "Español (España)"}
        ]


settings = Settings()