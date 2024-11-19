"""
Configuración de la aplicación.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings
from pydantic_settings import BaseSettings, SettingsError
from pydantic import field_validator, Field

class Settings(BaseSettings):
    PROJECT_NAME: str
    PROJECT_DESCRIPTION: str
    VERSION: str
    API_V1_STR: str
    BACKEND_CORS_ORIGINS: List[str] = Field(default=["http://localhost:8000"])
    ENABLE_METRICS: bool
    PROMETHEUS_PORT: int
    GRAFANA_PORT: int
    GRAFANA_ADMIN_PASSWORD: str
    BACKEND_PORT: int
    ENABLE_WHATSAPP_CALLBACK: bool
    MOCK_EXTERNAL_SERVICES: bool
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_URL: str
    SECRET_KEY: str
    ANTHROPIC_API_KEY: str
    WHATSAPP_CALLBACK_TOKEN: str
    WHATSAPP_PROVIDER: str
    FRONTEND_PORT: int
    VITE_API_URL: str

    class Config:
        env_file = ".env-development"
        env_file_encoding = "utf-8"

    @classmethod
    def parse_cors_origins(cls, value: str) -> List[str]:
        return [url.strip() for url in value.split(",") if url.strip()]

    def print_settings(self):
        model_dump = self.model_dump()
        print(f"Settings cargados: {model_dump}")

@lru_cache
def get_settings():
    settings = Settings()
    # Transformar BACKEND_CORS_ORIGINS si es necesario
    if isinstance(settings.BACKEND_CORS_ORIGINS, str):
        settings.BACKEND_CORS_ORIGINS = Settings.parse_cors_origins(
            settings.BACKEND_CORS_ORIGINS
        )
    return settings

settings = get_settings()
