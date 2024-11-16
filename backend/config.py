from typing import List, Union, Dict, Optional, Any
from pathlib import Path

from pydantic import PostgresDsn, field_validator, ValidationInfo, AnyHttpUrl
from pydantic_settings import BaseSettings


class LogConfig:
    """Configuración de logging"""

    LOGGER_NAME: str = "backend"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = "DEBUG"

    @classmethod
    def dict(cls) -> dict:
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "()": "uvicorn.logging.DefaultFormatter",
                    "fmt": cls.LOG_FORMAT,
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr",
                },
                "file": {
                    "formatter": "default",
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": "backend.log",
                    "maxBytes": 10000000,
                    "backupCount": 5,
                },
            },
            "loggers": {
                cls.LOGGER_NAME: {
                    "handlers": ["default", "file"],
                    "level": cls.LOG_LEVEL,
                },
            },
        }


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Attendance System"
    VERSION: str = "0.1.0"
    project_description: str = "Sistema de gestión de ausencias escolares"
    BACKEND_PORT: str = "8000"
    FRONTEND_PORT: str = "3000"
    VITE_API_URL: str = "http://localhost:8000/api/v1"

    # Environment
    APP_ENV: str = "development"
    DEBUG: bool = True
    PROJECT_ROOT: Path = Path(__file__).parent.parent

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:5173",
    ]

    @field_validator("BACKEND_CORS_ORIGINS")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "attendance"
    DATABASE_URI: Optional[PostgresDsn] = None

    @field_validator("DATABASE_URI")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            username=info.data.get("POSTGRES_USER"),
            password=info.data.get("POSTGRES_PASSWORD"),
            host=info.data.get("POSTGRES_SERVER"),
            port=int(info.data.get("POSTGRES_PORT", 5432)),  # Asegurar que es int
            path=f"/{info.data.get('POSTGRES_DB') or ''}",
        )

    # JWT
    SECRET_KEY: str = "your-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # External Services
    ANTHROPIC_API_KEY: str = ""
    DEV_ANTHROPIC_API_KEY: Optional[str] = None
    META_API_KEY: Optional[str] = None
    WHATSAPP_CALLBACK_TOKEN: Optional[str] = None
    WHATSAPP_PROVIDER: str = "mock"
    ENABLE_WHATSAPP: bool = False
    MOCK_EXTERNAL_SERVICES: bool = True

    # Cache & Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: str = "6379"
    REDIS_URL: Optional[str] = None
    CACHE_TTL_SECONDS: int = 3600  # 1 hour

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Monitoring
    SENTRY_DSN: Optional[str] = None
    ENABLE_METRICS: bool = True
    PROMETHEUS_PORT: str = "9090"
    GRAFANA_PORT: str = "3001"
    GRAFANA_ADMIN_PASSWORD: str = "admin"

    # Internationalization
    DEFAULT_LANGUAGE: str = "es-ES"
    SUPPORTED_LANGUAGES: List[str] = ["en-US", "es-ES"]

    class Config:
        case_sensitive = True
        env_file = ".env-dev"
        env_file_encoding = "utf-8"
        extra = "ignore"

    def get_supported_languages(self) -> List[Dict[str, str]]:
        return [
            {"code": "en-US", "name": "English (US)"},
            {"code": "es-ES", "name": "Español (España)"},
        ]


settings = Settings()
