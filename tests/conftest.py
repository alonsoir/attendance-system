import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from typing import Generator, Dict, Any
import json
from datetime import datetime, timedelta

from attendance_system.db.base import Base
from attendance_system.db.session import get_db
from attendance_system.core.config import settings
from attendance_system.main import app
from attendance_system.core.security import get_password_hash

# Crear base de datos de prueba
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_db():
    """Fixture que crea una base de datos de prueba y la limpia después de las pruebas."""
    Base.metadata.create_all(bind=engine)
    yield engine
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
    from attendance_system.db.models import User
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email
    }

@pytest.fixture
def test_interaction(db_session, test_user) -> Dict[str, Any]:
    """Fixture que crea una interacción de prueba."""
    from attendance_system.db.models import Interaction
    interaction = Interaction(
        student_name="Test Student",
        tutor_phone="+34666777888",
        status="active",
        sensitivity_score=5,
        claude_response={
            "sensitivity": 5,
            "response": "Test response",
            "likely_to_be_on_leave_tomorrow": False,
            "reach_out_tomorrow": True
        },
        created_by_id=test_user["id"]
    )
    db_session.add(interaction)
    db_session.commit()
    db_session.refresh(interaction)
    return {
        "id": interaction.id,
        "student_name": interaction.student_name,
        "tutor_phone": interaction.tutor_phone,
        "status": interaction.status
    }

@pytest.fixture
def mock_claude_response() -> Dict[str, Any]:
    """Fixture que proporciona una respuesta simulada de Claude."""
    return {
        "sensitivity": 7,
        "response": "The student is not feeling well.",
        "likely_to_be_on_leave_tomorrow": True,
        "reach_out_tomorrow": True
    }

@pytest.fixture
def mock_whatsapp_message() -> Dict[str, Any]:
    """Fixture que proporciona un mensaje simulado de WhatsApp."""
    return {
        "student_name": "Test Student",
        "tutor_phone": "+34666777888",
        "message": "El estudiante está enfermo hoy."
    }

@pytest.fixture
def mock_service_status() -> Dict[str, Any]:
    """Fixture que proporciona un estado simulado de servicios externos."""
    return {
        "claude": True,
        "meta": True
    }