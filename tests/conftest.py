import asyncio
import os
from typing import Any, Dict, Generator

import httpx
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend import get_settings
from backend.core.config import Settings
from backend.core.security import get_password_hash
from backend.db.base import Base
from backend.db.models import User, Interaction
from backend.db.session import get_db, create_engine
from backend.main import app

# Configuración y variables de entorno
os.environ["APP_ENV"] = "development"
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
async_engine: AsyncEngine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
AsyncTestingSessionLocal = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)

# ---- Fixtures globales ----
@pytest.fixture(scope="session", autouse=True)
def load_env():
    """Carga las variables de entorno desde el archivo .env."""
    env_path = os.path.join(os.path.dirname(__file__), "../.env-development")
    load_dotenv(env_path)

def test_pytest_configure():
    env_path = os.path.join(os.getcwd(), '.env-development')
    load_dotenv(dotenv_path=env_path)

def test_settings():
    settings = get_settings()
    assert settings.PROJECT_NAME == "Attendance System (Dev)"
    assert settings.API_V1_STR == "/api/v1"
    assert settings.PROJECT_DESCRIPTION == "Attendance System (Dev)"
    assert settings.VERSION == "0.1.0"
    assert settings.BACKEND_CORS_ORIGINS == "http://localhost:8000"
    assert settings.ENABLE_METRICS == True
    assert settings.PROMETHEUS_PORT == 9090
    assert settings.GRAFANA_PORT == 3000
    assert settings.GRAFANA_ADMIN_PASSWORD == "admin"
    assert settings.BACKEND_PORT == 8000
    assert settings.ENABLE_WHATSAPP_CALLBACK == True
    assert settings.MOCK_EXTERNAL_SERVICES == True
    assert settings.POSTGRES_SERVER == "localhost"
    assert settings.POSTGRES_USER == "user"
    assert settings.POSTGRES_PASSWORD == "password"
    assert settings.POSTGRES_DB == "database"
    assert settings.POSTGRES_PORT == 5432
    assert settings.REDIS_HOST == "localhost"
    assert settings.REDIS_PORT == 6379
    assert settings.REDIS_URL == "redis://localhost:6379"
    assert settings.SECRET_KEY != ""
    assert settings.ANTHROPIC_API_KEY != ""
    assert settings.WHATSAPP_CALLBACK_TOKEN == "your_callback_token"
    assert settings.WHATSAPP_PROVIDER == "provider_name"
    assert settings.FRONTEND_PORT == 3000
    assert settings.VITE_API_URL == "http://localhost:3000"


@pytest.fixture(autouse=True)
def set_env_variables():
    """Verifica que las variables de entorno necesarias estén disponibles."""
    required_env_vars = [
        "PROJECT_NAME", "PROJECT_DESCRIPTION", "VERSION", "API_V1_STR", "BACKEND_CORS_ORIGINS", "ENABLE_METRICS",
        "PROMETHEUS_PORT", "GRAFANA_PORT", "GRAFANA_ADMIN_PASSWORD", "BACKEND_PORT", "ENABLE_WHATSAPP_CALLBACK",
        "MOCK_EXTERNAL_SERVICES", "POSTGRES_SERVER", "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB",
        "POSTGRES_PORT", "REDIS_HOST", "REDIS_PORT", "REDIS_URL", "SECRET_KEY",
        "ANTHROPIC_API_KEY", "WHATSAPP_CALLBACK_TOKEN", "WHATSAPP_PROVIDER",
        "FRONTEND_PORT", "VITE_API_URL"
    ]

    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        pytest.fail(f"Las siguientes variables de entorno faltan: {', '.join(missing_vars)}")

    print("Variables de entorno cargadas correctamente.")


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    """Crea un loop de eventos para pytest-asyncio."""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


# ---- Fixtures de configuración ----
@pytest.fixture
def settings_dev():
    """Carga configuraciones desde `.env-development`."""
    return Settings(APP_ENV="development")


@pytest.fixture
def settings_prod():
    """Carga configuraciones desde `.env-production`."""
    return Settings(APP_ENV="prod")


# ---- Fixtures de base de datos ----
@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Inicializa y limpia las tablas de la base de datos para cada sesión de pruebas."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
def test_db():
    """Fixture que crea una base de datos de prueba y la limpia después de las pruebas."""
    Base.metadata.create_all(bind=create_engine(SQLALCHEMY_DATABASE_URL))
    yield async_engine
    Base.metadata.drop_all(bind=create_engine(SQLALCHEMY_DATABASE_URL))


@pytest.fixture
async def db_session():
    """Proporciona una sesión asíncrona de base de datos para las pruebas."""
    async with AsyncTestingSessionLocal() as session:
        yield session


# ---- Fixtures de cliente FastAPI ----
@pytest.fixture
async def async_client(db_session: AsyncSession):
    """Cliente asíncrono de pruebas para FastAPI."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def client(db_session) -> Generator:
    """Fixture que proporciona un cliente de prueba para la API."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ---- Fixtures de datos de prueba ----
@pytest.fixture
async def test_user(db_session: AsyncSession) -> Dict[str, Any]:
    """Fixture que crea un usuario de prueba de forma asíncrona."""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return {"id": user.id, "username": user.username, "email": user.email}


@pytest.fixture
async def test_interaction(db_session: AsyncSession, test_user: Dict[str, Any]) -> Dict[str, Any]:
    """Fixture que crea una interacción de prueba de forma asíncrona."""
    interaction = Interaction(
        student_name="Test Student",
        tutor_phone="+34666777888",
        status="active",
        sensitivity_score=5,
        claude_response={
            "sensitivity": 5,
            "response": "Test response",
            "likely_to_be_on_leave_tomorrow": False,
            "reach_out_tomorrow": True,
        },
        created_by_id=test_user["id"],
    )
    db_session.add(interaction)
    await db_session.commit()
    await db_session.refresh(interaction)
    return {
        "id": interaction.id,
        "student_name": interaction.student_name,
        "tutor_phone": interaction.tutor_phone,
        "status": interaction.status,
    }


@pytest.fixture
def mock_claude_response() -> Dict[str, Any]:
    """Fixture que proporciona una respuesta simulada de Claude."""
    return {
        "sensitivity": 7,
        "response": "The student is not feeling well.",
        "likely_to_be_on_leave_tomorrow": True,
        "reach_out_tomorrow": True,
    }


@pytest.fixture
def mock_whatsapp_message() -> Dict[str, Any]:
    """Fixture que proporciona un mensaje simulado de WhatsApp."""
    return {
        "student_name": "Test Student",
        "tutor_phone": "+34666777888",
        "message": "El estudiante está enfermo hoy.",
    }


@pytest.fixture
def mock_service_status() -> Dict[str, Any]:
    """Fixture que proporciona un estado simulado de servicios externos."""
    return {"claude": True, "meta": True}
