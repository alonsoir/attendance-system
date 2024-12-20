import asyncio
import os
from pathlib import Path
from typing import Any, Dict, Generator
from unittest.mock import AsyncMock

import httpx
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.core.config import Settings, get_settings
from backend.db.models import Base
from backend.db.session import create_engine, get_db
from backend.main import app
from backend.services.attendance import AttendanceManager
from backend.services.whatsapp import WhatsAppService

# Configuración y variables de entorno
os.environ["APP_ENV"] = "development"
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


import logging


# @pytest.fixture(scope="session")
def pytest_configure():
    logging.basicConfig(level=logging.ERROR)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)
    logging.getLogger("faker.factory").setLevel(logging.ERROR)
    logging.getLogger("aiosqlite").setLevel(logging.ERROR)
    # Si quieres silenciar completamente
    logging.getLogger("sqlalchemy.engine.Engine").setLevel(logging.ERROR)


@pytest.fixture(scope="session")
async def async_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, echo=True
    )

    # Crear las tablas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Limpiar después de todas las pruebas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(async_engine) -> AsyncSession:
    """Provide a database session for testing."""
    async_session = async_sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


@pytest.fixture(scope="session")
async def asyncTestingSessionLocal():
    asyncTestingSessionLocal = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )
    yield asyncTestingSessionLocal


@pytest.fixture(scope="session")
async def whatsapp_service():
    settings = Settings()
    # Instancia única de WhatsAppService (Singleton)
    service = WhatsAppService(
        provider=settings.WHATSAPP_PROVIDER,
        meta_api_key=settings.WHATSAPP_META_API_KEY,
        callback_token=settings.WHATSAPP_CALLBACK_TOKEN,
    )
    await service.init_service()  # Inicializar el cliente HTTP
    yield service  # Proveer la instancia a las pruebas
    await service.close_service()  # Cerrar después de las pruebas


@pytest.fixture(autouse=True)
def mock_logging(monkeypatch):
    pass


@pytest.fixture(scope="session")
def attendance_manager():
    """Fixture para el Singleton AttendanceManager."""
    return AttendanceManager()


"""
@pytest.mark.asyncio
async def test_singleton_instance(whatsapp_service):
    # Obtener otra instancia del servicio
    another_service = WhatsAppService(provider="callmebot")
    another_service.init_service()
    # Verificar que ambas instancias son la misma (singleton)
    assert whatsapp_service is another_service
    another_service.close_service()
    whatsapp_service.close_service()
"""


@pytest.fixture(scope="session", autouse=True)
def load_env_development():
    """Carga las variables de entorno desde el archivo .env."""
    env_path = Path(__file__).resolve().parent.parent / ".env-development"
    if not os.path.exists(env_path):
        raise FileNotFoundError(f"No se encontró el archivo .env en {env_path}")

    load_dotenv(env_path, override=True)
    print("Cargando variables de entorno (.env-development)...")
    for key, value in os.environ.items():
        if os.getenv(key) == "Attendance System (Dev)":
            print(f"{os.getenv(key)} = {value} found!")
            assert os.getenv(key) == "Attendance System (Dev)"


# Fixtures globales y configuración
@pytest.fixture(scope="session", autouse=True)
def test_project_name():
    settings = Settings()
    assert (
        settings.PROJECT_NAME == "Attendance System (Dev)"
    ), f"Valor obtenido: {settings.PROJECT_NAME}"


@pytest.fixture(scope="session", autouse=True)
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
    assert settings.POSTGRES_USER == "test_user"
    assert settings.POSTGRES_PASSWORD == "test_password"
    assert settings.POSTGRES_DB == "test_db"
    assert settings.POSTGRES_PORT == 5432
    assert settings.REDIS_HOST == "localhost"
    assert settings.REDIS_PORT == 6379
    assert settings.REDIS_URL == "redis://localhost:6379"
    assert settings.SECRET_KEY != ""
    assert settings.ANTHROPIC_API_KEY != ""
    assert settings.WHATSAPP_META_API_KEY != ""
    assert settings.WHATSAPP_CALLBACK_TOKEN == "9295095"
    assert settings.WHATSAPP_PROVIDER == "callmebot"
    assert settings.FRONTEND_PORT == 3000
    assert settings.VITE_API_URL == "http://localhost:3000"


@pytest.fixture(scope="session", autouse=True)
def event_loop():
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


@pytest.fixture(scope="session", autouse=True)
async def setup_database(async_engine):
    """
    Inicializa y limpia las tablas de la base de datos para cada sesión de pruebas.

    Este fixture crea todas las tablas definidas en los modelos de SQLAlchemy antes
    de ejecutar las pruebas, y las elimina al final de la sesión para mantener un
    entorno limpio.
    """
    async with async_engine.begin() as conn:
        # Crear todas las tablas antes de ejecutar las pruebas
        await conn.run_sync(Base.metadata.create_all)
        print("Tablas creadas exitosamente para la sesión de pruebas.")

    yield  # Aquí se ejecutan las pruebas que dependen de la base de datos

    async with async_engine.begin() as conn:
        # Eliminar todas las tablas después de ejecutar las pruebas
        await conn.run_sync(Base.metadata.drop_all)
        print("Tablas eliminadas exitosamente después de la sesión de pruebas.")


@pytest.fixture(scope="session")
def test_db():
    """Fixture que crea una base de datos de prueba y la limpia después de las pruebas."""
    Base.metadata.create_all(bind=create_engine(SQLALCHEMY_DATABASE_URL))
    yield async_engine
    Base.metadata.drop_all(bind=create_engine(SQLALCHEMY_DATABASE_URL))


@pytest.fixture
async def db_session(async_engine):
    async_session = async_sessionmaker(async_engine, expire_on_commit=False)
    async with async_session() as session:
        yield session  # Esto debería retornar un objeto de tipo AsyncSession


async def test_db_session_fixture(db_session):
    assert isinstance(db_session, AsyncSession)


@pytest.fixture
def mock_callmebot_client():
    client = AsyncMock()
    client.send_message.return_value = {"status": "success"}
    return client


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
"""
@pytest.fixture
async def test_user(db_session: AsyncSession) -> Dict[str, Any]:
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
async def test_interaction(
    db_session: AsyncSession, test_user: Dict[str, Any]
) -> Dict[str, Any]:
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
"""


@pytest.fixture
def mock_claude_response() -> Dict[str, Any]:
    """Fixture que proporciona una respuesta simulada de Claude."""
    return AsyncMock(return_value={"message": "Test response"})


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
