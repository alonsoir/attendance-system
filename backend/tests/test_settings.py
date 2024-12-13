from typing import List
from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    # Información del proyecto
    PROJECT_NAME: str = "Test Attendance System"
    PROJECT_DESCRIPTION: str = "Test Environment for Attendance System"
    VERSION: str = "0.1.0"

    # API y Backend
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: str = "http://localhost:8000"
    BACKEND_PORT: int = 8000

    # Monitorización
    ENABLE_METRICS: bool = False
    PROMETHEUS_PORT: int = 9090
    GRAFANA_PORT: int = 3000
    GRAFANA_ADMIN_PASSWORD: str = "admin"

    # Base de datos PostgreSQL
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "test_user"
    POSTGRES_PASSWORD: str = "test_password"
    POSTGRES_DB: str = "test_db"
    POSTGRES_PORT: int = 5432

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: str = "redis://localhost:6379"

    # Seguridad
    SECRET_KEY: str = "test_secret_key_for_testing_purposes_only"

    # Servicios externos
    ANTHROPIC_API_KEY: str = "test_anthropic_key"
    WHATSAPP_CALLBACK_TOKEN: str = "test_whatsapp_token"
    WHATSAPP_META_API_KEY: str = "test_whatsapp_api_key"
    WHATSAPP_PROVIDER: str = "mock"  # Usar un provider mock para pruebas

    # Frontend
    FRONTEND_PORT: int = 3000
    VITE_API_URL: str = "http://localhost:8000"

    # Flags de control para pruebas
    ENABLE_WHATSAPP_CALLBACK: bool = False
    MOCK_EXTERNAL_SERVICES: bool = True

    class Config:
        case_sensitive = True
        env_file = ".env.test"


def get_test_settings() -> TestSettings:
    """Función helper para obtener las configuraciones de prueba"""
    return TestSettings()