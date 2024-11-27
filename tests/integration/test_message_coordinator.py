from datetime import datetime
from unittest.mock import patch

import pytest
from sqlalchemy import text, select

from backend.db import get_db
from backend.services.message_coordinator import MessageCoordinator


@pytest.fixture(autouse=True)
async def setup_teardown():
    """Fixture para setup y teardown de los tests."""
    # Setup - usar SQLite en memoria para los tests
    from sqlalchemy.ext.asyncio import create_async_engine
    from backend.db.base import Base

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Teardown
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def coordinator():
    coordinator = MessageCoordinator.get_instance()
    yield coordinator
    await coordinator.cleanup()


@pytest.fixture
def valid_message_data():
    return {
        "student_name": "Test Student",
        "tutor_phone": "+34666777888",
        "message_content": "El estudiante está enfermo hoy",
        "tutor_name": "Test Parent",
        "timestamp": datetime.now(),
    }


@pytest.mark.integration
@pytest.mark.asyncio
async def test_message_coordinator_end_to_end(coordinator, valid_message_data):
    """Test de integración completo del flujo de mensajes."""

    async def mock_response_callback(phone: str, message: str):
        assert phone == valid_message_data["tutor_phone"]
        assert isinstance(message, str)
        return {"status": "sent", "phone": phone}

    with patch(
        "backend.services.attendance.AttendanceManager.process_whatsapp_message"
    ) as mock_process:
        mock_process.return_value = {
            "status": "success",
            "response": "Test response",
            "claude_response": {"sensitivity": 5, "response": "Test response"},
        }

        result = await coordinator.process_message(
            valid_message_data, mock_response_callback
        )

        mock_process.assert_called_once()
        assert result["status"] == "success"
        assert "timestamp" in result
        assert result["processing_completed"] is True


@pytest.mark.integration
@pytest.mark.asyncio
async def test_message_coordinator_with_claude_integration(coordinator):
    """Test de integración con el servicio Claude."""
    message_data = {
        "student_name": "Test Student",
        "tutor_phone": "+34666777888",
        "message_content": "El estudiante tiene fiebre alta",
        "tutor_name": "Test Parent",
    }

    async def mock_response_callback(phone: str, message: str):
        return {"status": "sent"}

    with patch(
        "backend.services.attendance.AttendanceManager.process_whatsapp_message"
    ) as mock_process:
        # Configurar el mock para simular una respuesta con alta sensibilidad
        mock_process.return_value = {
            "status": "success",
            "response": "Se atenderá la situación de fiebre alta",
            "claude_response": {
                "sensitivity": 8,
                "response": "Entiendo la gravedad de la situación",
                "likely_to_be_on_leave_tomorrow": True,
                "reach_out_tomorrow": True,
            },
        }

        result = await coordinator.process_message(message_data, mock_response_callback)

        assert result["status"] == "success"
        assert isinstance(result.get("claude_response"), dict)
        assert "sensitivity" in result.get("claude_response", {})
        assert (
            result.get("claude_response", {}).get("sensitivity", 0) >= 7
        )  # Alta sensibilidad por fiebre


@pytest.mark.integration
@pytest.mark.asyncio
async def test_message_coordinator_persistence(coordinator, valid_message_data):
    """Test de integración verificando la persistencia en base de datos."""
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from backend.db.base import Base
    from backend.db.models import Interaction

    # Crear engine SQLite en memoria para tests
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=True)
    TestingSessionLocal = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    # Setup: crear tablas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Crear una sesión de prueba
    test_session = TestingSessionLocal()

    # Parchear el método que obtiene la sesión en AttendanceManager
    async def get_test_session():
        return test_session

    with patch("backend.services.attendance.get_db", new=get_test_session):

        async def mock_response_callback(phone: str, message: str):
            return {"status": "sent"}

        with patch(
            "backend.services.attendance.AttendanceManager.process_whatsapp_message"
        ) as mock_process:
            # Crear una interacción directamente en la base de datos
            interaction = Interaction(
                id=1,
                student_name=valid_message_data["student_name"],
                tutor_phone=valid_message_data["tutor_phone"],
                status="active",
                sensitivity_score=5,
                claude_response={
                    "sensitivity": 5,
                    "response": "Test response",
                    "likely_to_be_on_leave_tomorrow": False,
                    "reach_out_tomorrow": False,
                },
            )
            test_session.add(interaction)
            await test_session.commit()

            mock_process.return_value = {
                "status": "success",
                "response": "Mensaje procesado",
                "interaction_id": interaction.id,
                "claude_response": interaction.claude_response,
            }

            # Ejecutar el proceso
            result = await coordinator.process_message(
                valid_message_data, mock_response_callback
            )

            assert result["status"] == "success"
            assert "interaction_id" in result

            # Verificar en la base de datos
            stmt = select(Interaction).where(Interaction.id == result["interaction_id"])
            result_db = await test_session.execute(stmt)
            db_interaction = result_db.scalar_one_or_none()

            assert db_interaction is not None
            assert db_interaction.student_name == valid_message_data["student_name"]
            assert db_interaction.tutor_phone == valid_message_data["tutor_phone"]

    # Cleanup
    await test_session.close()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_message_coordinator_high_sensitivity_scenario(coordinator):
    """Test de integración para mensajes de alta sensibilidad."""
    emergency_message = {
        "student_name": "Test Student",
        "tutor_phone": "+34666777888",
        "message_content": "Emergencia médica: el estudiante necesita atención inmediata",
        "tutor_name": "Test Parent",
    }

    async def mock_response_callback(phone: str, message: str):
        return {"status": "sent"}

    # Mock de AttendanceManager
    with patch(
        "backend.services.attendance.AttendanceManager.process_whatsapp_message"
    ) as mock_process:
        # Simular una respuesta de alta sensibilidad
        mock_process.return_value = {
            "status": "success",
            "response": "Atendiendo emergencia médica",
            "claude_response": {
                "sensitivity": 9,  # Alta sensibilidad por ser emergencia médica
                "response": "Entendido, situación de emergencia médica",
                "likely_to_be_on_leave_tomorrow": True,
                "reach_out_tomorrow": True,
            },
        }

        result = await coordinator.process_message(
            emergency_message, mock_response_callback
        )

        assert result["status"] == "success"
        claude_response = result.get("claude_response", {})
        assert (
            claude_response.get("sensitivity", 0) >= 8
        )  # Alta sensibilidad para emergencias


@pytest.mark.integration
@pytest.mark.asyncio
async def test_message_coordinator_concurrent_processing(coordinator):
    """Test de integración para procesamiento concurrente."""
    messages = [
        {
            "student_name": f"Student {i}",
            "tutor_phone": "+34666777888",
            "message_content": f"Test message {i}",
            "tutor_name": f"Parent {i}",
        }
        for i in range(3)
    ]

    async def mock_response_callback(phone: str, message: str):
        return {"status": "sent"}

    # Mock de AttendanceManager para procesamiento concurrente
    with patch(
        "backend.services.attendance.AttendanceManager.process_whatsapp_message"
    ) as mock_process:

        def create_mock_response(message_data):
            return {
                "status": "success",
                "response": f"Processed message for {message_data['student_name']}",
                "interaction_id": id(message_data),  # Usar id() para generar IDs únicos
                "claude_response": {
                    "sensitivity": 5,
                    "response": "Test response",
                    "likely_to_be_on_leave_tomorrow": False,
                    "reach_out_tomorrow": False,
                },
            }

        # Configurar el mock para devolver respuestas únicas para cada mensaje
        mock_process.side_effect = lambda message_data: create_mock_response(
            message_data
        )

        import asyncio

        tasks = [
            coordinator.process_message(msg, mock_response_callback) for msg in messages
        ]

        results = await asyncio.gather(*tasks)

        # Verificaciones
        assert all(r["status"] == "success" for r in results)
        # Verificar que todos los IDs son únicos
        interaction_ids = [r.get("interaction_id") for r in results]
        assert len(set(interaction_ids)) == len(messages)
        # Verificar que se procesaron todos los mensajes
        assert mock_process.call_count == len(messages)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_message_coordinator_recovery_scenario(coordinator):
    """Test de integración para escenario de recuperación tras error."""
    message_data = {
        "student_name": "Test Student",
        "tutor_phone": "+34666777888",
        "message_content": "Test message",
        "tutor_name": "Test Parent",
    }

    call_count = 0

    async def failing_callback(phone: str, message: str):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise Exception("Simulated network error")
        return {"status": "sent"}

    # Mock de AttendanceManager
    with patch(
        "backend.services.attendance.AttendanceManager.process_whatsapp_message"
    ) as mock_process:
        mock_process.return_value = {
            "status": "success",
            "response": "Mensaje procesado",
            "claude_response": {
                "sensitivity": 5,
                "response": "Test response",
                "likely_to_be_on_leave_tomorrow": False,
                "reach_out_tomorrow": False,
            },
        }

        result = await coordinator.process_message(message_data, failing_callback)

        assert result["status"] == "success"
        assert "warning" in result
        assert "response delivery failed" in result["warning"]
        assert call_count == 1  # Verifica que el callback falló una vez
        mock_process.assert_called_once()  # Verifica que AttendanceManager fue llamado una vez
