"""
Configuración de la aplicación.
"""
import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str
    PROJECT_DESCRIPTION: str
    VERSION: str
    API_V1_STR: str
    BACKEND_CORS_ORIGINS: str
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
    WHATSAPP_META_API_KEY: str
    WHATSAPP_PROVIDER: str
    FRONTEND_PORT: int
    VITE_API_URL: str
    # todo refactorize this to load different settings for each environment
    model_config = SettingsConfigDict(env_file=".env")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not os.path.exists(".env"):
            raise FileNotFoundError("El archivo .env no se encontró")

    def print_settings(self):
        model_dump = self.model_dump()
        print(f"Settings cargados(backend/core/config.py): {model_dump}")


@lru_cache
def get_settings():
    settings = Settings()
    settings.print_settings()
    return settings
