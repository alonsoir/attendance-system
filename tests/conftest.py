import os
from typing import Any, Dict, Generator

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.config import Settings
from backend.core.security import get_password_hash

# 1. Establece APP_ENV antes de cargar el .env
os.environ['APP_ENV'] = 'development'

# 2. Carga las variables de entorno desde .env-development
load_dotenv(".env-development")

# Crear base de datos de prueba
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def load_env():
    env_path = os.path.join(os.path.dirname(__file__), "../.env-development")
    load_dotenv(env_path)

@pytest.fixture(autouse=True)
def set_env_variables():
    """Verifica que las variables de entorno necesarias estén disponibles."""
    required_env_vars = [
        "POSTGRES_SERVER", "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB",
        "POSTGRES_PORT", "REDIS_HOST", "REDIS_PORT", "REDIS_URL", "SECRET_KEY",
        "ANTHROPIC_API_KEY", "WHATSAPP_CALLBACK_TOKEN", "WHATSAPP_PROVIDER",
        "FRONTEND_PORT", "VITE_API_URL"
    ]

    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        missing = ", ".join(missing_vars)
        pytest.fail(f"Las siguientes variables de entorno faltan: {missing}")

    # Opcional: Imprimir para depuración
    print("Variables de entorno cargadas correctamente desde .env-development.")


@pytest.fixture
def settings_dev():
    """Carga configuraciones desde `.env-development`."""
    return Settings(APP_ENV="dev")


def test_env_dev_loaded(settings_dev):
    assert os.environ.get("POSTGRES_USER") == "postgres"
    assert os.environ.get("POSTGRES_PASSWORD") == "postgres"
    assert os.environ.get("POSTGRES_SERVER") == "localhost"
    assert os.environ.get("POSTGRES_PORT") == "5432"
    assert os.environ.get("POSTGRES_DB") == "attendance_dev"
    assert os.environ.get("SECRET_KEY") == "secret_key"
    assert os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES") == "60"
    assert os.environ.get("ALGORITHM") == "HS256"
    assert os.environ.get("BACKEND_CORS_ORIGINS") == "http://localhost:3000"
    assert os.environ.get("BACKEND_PORT") == "8000"
    assert (
        os.environ.get("DATABASE_URI")
        == "postgresql://postgres:postgres@localhost:5432/attendance_dev"
    )


def test_settings_dev(settings_dev):
    assert settings_dev.APP_ENV == "dev"
    assert settings_dev.DEBUG is True  # O el valor esperado


load_dotenv(".env-production")


@pytest.fixture
def settings_prod():
    """Carga configuraciones desde `.env-production`."""
    return Settings(APP_ENV="prod")


def test_settings_prod(settings_prod):
    assert settings_prod.APP_ENV == "prod"


from backend.db.base import Base
from backend.db.session import (
    get_db,
)
from backend.db.session import engine

from backend.main import app

import asyncio

import pytest
from backend.db.session import get_db_context, check_database_connection, init_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.db.models import ServiceStatus


@pytest.mark.asyncio
async def test_get_db_context():
    """Prueba que `get_db_context` devuelve una sesión válida."""
    async with get_db_context() as db:
        assert isinstance(db, AsyncSession), "Se esperaba una instancia de AsyncSession"
        # Verificar que la sesión puede ejecutar una consulta
        result = await db.execute(select(ServiceStatus))
        assert result is not None, "La consulta no devolvió resultados"


@pytest.mark.asyncio
async def test_check_database_connection():
    """Prueba la conexión a la base de datos."""
    is_connected = await check_database_connection()
    assert is_connected, "No se pudo conectar a la base de datos"


@pytest.mark.asyncio
async def test_init_db():
    """Prueba que la base de datos se inicializa correctamente con datos predeterminados."""
    # Inicializamos la base de datos
    await init_db()

    # Verificamos que los estados de servicio se hayan creado correctamente
    async with get_db_context() as db:
        result = await db.execute(select(ServiceStatus).filter_by(service_name="claude"))
        service_status = await result.scalars().first()
        assert service_status is not None, "El estado de servicio 'claude' no fue creado"
        assert service_status.status is True, "El estado de servicio 'claude' no tiene el estado correcto"

        result = await db.execute(select(ServiceStatus).filter_by(service_name="meta"))
        service_status = await result.scalars().first()
        assert service_status is not None, "El estado de servicio 'meta' no fue creado"
        assert service_status.status is True, "El estado de servicio 'meta' no tiene el estado correcto"


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    """Crea un loop de eventos para pytest-asyncio"""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


def test_database_connection(settings_dev, test_db):
    # Aquí puedes interactuar con la base de datos para verificar que se ha creado correctamente
    assert test_db is not None


@pytest.fixture(scope="session")
def test_db():
    """Fixture que crea una base de datos de prueba y la limpia después de las pruebas."""
    # Crea la base de datos
    Base.metadata.create_all(bind=engine)
    yield engine
    # Limpia la base de datos después de las pruebas
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)  # Limpia todo
    Base.metadata.create_all(bind=engine)  # Crea todas las tablas
    yield
    Base.metadata.drop_all(bind=engine)  # Limpia al terminar


def test_setup_database(
    settings_dev, setup_database, create_test_db, db_session, client, test_user
):
    assert db_session is not None


@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    """Crea todas las tablas antes de los tests y las elimina después"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_db):
    """Fixture que proporciona una sesión de base de datos limpia para cada prueba."""
    connection = test_db.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


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


@pytest.fixture
def test_user(db_session) -> Dict[str, Any]:
    """Fixture que crea un usuario de prueba."""
    from backend.db.models import User

    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return {"id": user.id, "username": user.username, "email": user.email}


@pytest.fixture
def test_interaction(db_session, test_user) -> Dict[str, Any]:
    """Fixture que crea una interacción de prueba."""
    from backend.db.models import Interaction

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
    db_session.commit()
    db_session.refresh(interaction)
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
