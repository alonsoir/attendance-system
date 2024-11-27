import asyncio
import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from unittest.mock import MagicMock
from unittest.mock import patch, AsyncMock

import pytest
from aiohttp import ClientConnectionError, ServerTimeoutError
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from starlette.websockets import WebSocket

from backend import get_settings
from backend.db.models import ServiceStatus
from backend.services.claude import ClaudeService
from backend.services.claude import generate_claude_response
from backend.services.whatsapp import WhatsAppService, MessageProvider

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("faker.factory").setLevel(logging.WARNING)


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_send_message_to_callmebot():
    """Prueba el envío de mensajes de WhatsApp en modo mock con provider CallMeBot."""
    settings = get_settings()
    # Configuración del servicio

    service = WhatsAppService(
        provider=MessageProvider.CALLMEBOT,
        meta_api_key=None,
        callback_token=settings.WHATSAPP_CALLBACK_TOKEN,
    )
    await service.init_service()  # Inicializar el cliente HTTP

    phone = "+34667519829"
    message = "Hello, this is a test, from test_send_message_to_callmebot..."
    expected_url = (
        f"https://api.callmebot.com/whatsapp.php?"
        f"phone={phone}&text={message}&apikey=9295095"
    )

    mock_response_text = "Hello, this is a test, from test_send_message_to_callmebot..."

    # Mock de `aiohttp.ClientSession.get`
    with patch("aiohttp.ClientSession.get") as mock_get:
        # Configuración del mock para simular una respuesta exitosa
        mock_response = AsyncMock()
        mock_response.text = AsyncMock(return_value=mock_response_text)
        mock_response.status = 200

        mock_get.return_value.__aenter__.return_value = mock_response

        # Llamada a la función
        response = await service.send_message(phone=phone, message=message)

        assert (
            response.get("status") == "success"
            or response.get("phone") == phone
            or response.get("message") == message
        )

        await service.close_service()


# Tests para el servicio de WhatsApp
@pytest.mark.asyncio
@pytest.mark.unittest
async def test_send_whatsapp_message():
    """Prueba el envío de mensajes de WhatsApp con provider Meta. Verifica NotImplementedError."""
    service = WhatsAppService(provider=MessageProvider.META)
    await service.init_service()

    phone = "+34667519829"
    message = "Hello, this is a test..."

    with pytest.raises(
        NotImplementedError, match="Meta WhatsApp API not implemented yet"
    ):
        await service._send_meta_message(phone=phone, message=message)

    await service.close_service()


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_send_whatsapp_message_invalid_phone():
    """Prueba el envío de mensajes a números inválidos."""
    """Prueba el envío de mensajes de WhatsApp en modo mock con provider Meta."""
    # Configuración del servicio
    service = WhatsAppService(
        provider=MessageProvider.META, meta_api_key=None, callback_token=None
    )
    await service.init_service()

    with pytest.raises(ValueError):
        await service.send_message("invalid-phone", "Test message")
        await service.close_service()


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_send_whatsapp_message_invalid_phone():
    """Prueba el envío de mensajes a números inválidos."""
    """Prueba el envío de mensajes de WhatsApp en modo mock con provider CallMeBot."""
    # Configuración del servicio
    settings = get_settings()
    # Configuración del servicio

    service = WhatsAppService(
        provider=MessageProvider.CALLMEBOT,
        meta_api_key=None,
        callback_token=settings.WHATSAPP_CALLBACK_TOKEN,
    )
    await service.init_service()

    with pytest.raises(ValueError):
        await service.send_message("invalid-phone", "Test message")
        await service.close_service()


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_process_whatsapp_message(mock_whatsapp_message, attendance_manager):
    """Test processing of WhatsApp messages via AttendanceManager."""
    attendance_manager = AttendanceManager.get_instance()

    mock_message = {
        "student_name": "John Doe",
        "tutor_phone": "+34600111222",
    }

    expected_response = {
        "status": "success",
        "response": {
            "sensitivity": 5,
            "response": "Test response",
            "likely_to_be_on_leave_tomorrow": False,
            "reach_out_tomorrow": True,
        },
    }

    with patch.object(
        attendance_manager,
        "process_whatsapp_message",
        AsyncMock(return_value=expected_response),
    ):
        result = await attendance_manager.process_whatsapp_message(mock_message)
        assert result["status"] == "success"
        assert "response" in result
        assert result["response"]["response"] == "Test response"


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_verify_authorization():
    """Prueba la verificación de autorización."""
    manager = AttendanceManager.get_instance()
    result = await manager.verify_authorization(
        student_name="Test Student", tutor_phone="+34666777888"
    )

    assert result is True  # Ajustar según la lógica real de autorización


@pytest.fixture
def mock_db_session():
    """Fixture for mocking the database session."""
    session_mock = AsyncMock()
    session_mock.commit = AsyncMock()
    session_mock.rollback = AsyncMock()
    session_mock.add = AsyncMock()
    session_mock.execute = AsyncMock()
    yield session_mock


@pytest.fixture
def mock_websocket():
    """Fixture for mocking a WebSocket connection."""
    websocket_mock = AsyncMock(spec=WebSocket)
    yield websocket_mock


@pytest.fixture
def attendance_manager():
    """Fixture for providing a clean instance of AttendanceManager."""
    manager = AttendanceManager.get_instance()
    # Reset active connections for isolated tests
    manager.active_connections = {}
    return manager


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_process_whatsapp_message_success(
    attendance_manager, mock_db_session, mock_claude_response
):
    """Test successful processing of a WhatsApp message."""
    message_data = {"student_name": "John Doe", "tutor_phone": "+1234567890"}

    with patch("backend.services.attendance.get_db", return_value=mock_db_session):
        response = await attendance_manager.process_whatsapp_message(message_data)

    # Assertions
    assert response["status"] == "success"
    assert "response" in response


@pytest.mark.asyncio
async def test_process_whatsapp_message_incomplete_data(attendance_manager):
    """Test processing a WhatsApp message with incomplete data."""
    incomplete_message_data = {"student_name": "John Doe"}  # Missing tutor_phone

    response = await attendance_manager.process_whatsapp_message(
        incomplete_message_data
    )

    assert response["status"] == "error"
    assert "Incomplete data" in response["message"]


@pytest.mark.asyncio
@patch(
    "backend.services.attendance.AttendanceManager.verify_authorization",
    AsyncMock(return_value=False),
)
async def test_process_whatsapp_message_unauthorized(attendance_manager):
    """Test unauthorized access when processing a WhatsApp message."""
    message_data = {"student_name": "John Doe", "tutor_phone": "+1234567890"}

    response = await attendance_manager.process_whatsapp_message(message_data)

    assert response["status"] == "error"
    assert "Unauthorized access" in response["message"]


@pytest.mark.asyncio
@patch(
    "backend.services.attendance.generate_claude_response",
    AsyncMock(side_effect=Exception("API error")),
)
async def test_process_whatsapp_message_exception(attendance_manager):
    """Test handling an unexpected exception."""
    message_data = {"student_name": "John Doe", "tutor_phone": "+1234567890"}

    response = await attendance_manager.process_whatsapp_message(message_data)

    assert response["status"] == "error"
    assert "API error" in response["message"]


@pytest.mark.asyncio
async def test_process_whatsapp_message_incomplete_data(attendance_manager):
    """Test WhatsApp message processing with missing data."""
    message_data = {"student_name": "John Doe"}  # Missing tutor_phone

    with pytest.raises(ValueError) as exc_info:
        await attendance_manager.process_whatsapp_message(message_data)

    assert str(exc_info.value) == "invalid_phone"


@pytest.mark.asyncio
async def test_process_whatsapp_message_db_error(attendance_manager):
    """Test WhatsApp message processing with a database error."""

    # Create a mock session with all required async methods
    mock_session = AsyncMock()
    mock_session.commit = AsyncMock(side_effect=SQLAlchemyError("DB Error"))
    mock_session.rollback = AsyncMock()
    mock_session.add = AsyncMock()
    mock_session.close = AsyncMock()

    message_data = {"student_name": "John Doe", "tutor_phone": "+1234567890"}

    # Create a mock async session factory that mirrors the real implementation
    @asynccontextmanager
    async def mock_get_db():
        try:
            yield mock_session
        finally:
            await mock_session.close()

    # Patch get_db to return our mock session
    with patch("backend.services.attendance.get_db", return_value=mock_get_db()):
        # Simulate verify_authorization to return True
        with patch.object(
            attendance_manager, "verify_authorization", return_value=True
        ):
            # Simulate generate_claude_response
            with patch(
                "backend.services.attendance.generate_claude_response",
                return_value={"response": "Test response"},
            ):
                response = await attendance_manager.process_whatsapp_message(
                    message_data
                )

    # Verify error response
    assert (
        response["status"] == "error"
    ), f"Expected error status but got {response['status']}"
    assert (
        "DB Error" in response["message"]
    ), f"Expected 'DB Error' in message but got: {response['message']}"

    # Verify proper session usage
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_called_once()
    mock_session.close.assert_called_once()

    # Verify logging
    # (opcional) Podrías agregar verificaciones de logging si es importante para tu caso


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_edge_cases(attendance_manager):
    """Test edge cases in data handling."""
    test_cases = [
        ({"student_name": "", "tutor_phone": "+1234567890"}, "empty_name"),
        ({"student_name": "X" * 1000, "tutor_phone": "+1234567890"}, "name_too_long"),
        ({"student_name": "John", "tutor_phone": "+1"}, "invalid_phone"),
        ({"student_name": None, "tutor_phone": "+1234567890"}, "null_name"),
    ]

    for data, expected_error in test_cases:
        logger.debug(f"Testing case: {data} expecting error: {expected_error}")
        with pytest.raises(ValueError, match=expected_error) as exc_info:
            await attendance_manager.process_whatsapp_message(data)
        logger.debug(f"Received expected error: {str(exc_info.value)}")

    # Verificación opcional
    assert (
        not attendance_manager.active_connections
    ), "No deberían quedar conexiones activas"


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_network_errors():
    """Test network-related errors."""
    service = ClaudeService.get_instance()

    # Test timeout error
    with patch.object(service, "_session", new=None):  # Reset session
        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_post.side_effect = ServerTimeoutError("Connection timeout")

            response = await service.generate_response("Test", "Test message")
            assert "connection timeout" in str(response["response"]).lower()
            assert response["sensitivity"] == 5
            assert not response["likely_to_be_on_leave_tomorrow"]
            assert not response["reach_out_tomorrow"]

    # Test connection error
    with patch.object(service, "_session", new=None):  # Reset session
        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_post.side_effect = ClientConnectionError("Connection failed")

            response = await service.generate_response("Test", "Test message")
            assert "connection failed" in str(response["response"]).lower()
            assert response["sensitivity"] == 5
            assert not response["likely_to_be_on_leave_tomorrow"]
            assert not response["reach_out_tomorrow"]


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_concurrent_access():
    """Test concurrent access to shared resources."""
    service = ClaudeService.get_instance()

    mock_session = AsyncMock()
    mock_context = AsyncMock()
    mock_context.json.return_value = {
        "content": [
            {
                "text": '{"sensitivity": 5, "response": "Test response", "likely_to_be_on_leave_tomorrow": false, "reach_out_tomorrow": true}'
            }
        ]
    }
    mock_session.post.return_value = mock_context

    # Patch directamente el _session en lugar de get_session
    with patch.object(service, "_session", mock_session):
        # Ejecutar llamadas concurrentes
        responses = await asyncio.gather(
            service.generate_response("Test1", "Test message"),
            service.generate_response("Test2", "Test message"),
            service.generate_response("Test3", "Test message"),
        )

        # Verificar que todas las respuestas son válidas
        for response in responses:
            assert isinstance(response, dict)
            assert "sensitivity" in response
            assert "response" in response
            assert "likely_to_be_on_leave_tomorrow" in response
            assert "reach_out_tomorrow" in response

        # Verificar que se usó la misma sesión para todas las llamadas
        assert mock_session.post.call_count == 3


@pytest.mark.asyncio
async def test_broadcast_update_success(attendance_manager, mock_websocket):
    """Test successful broadcasting of updates to all connected clients."""
    attendance_manager.add_connection(1, mock_websocket)
    attendance_manager.add_connection(2, mock_websocket)

    with patch.object(
        attendance_manager, "get_dashboard_data", return_value={"test_data": "value"}
    ):
        await attendance_manager.broadcast_update()

    assert mock_websocket.send_json.call_count == 2


@pytest.mark.asyncio
async def test_broadcast_update_connection_error(attendance_manager, mock_websocket):
    """Test broadcasting updates with a connection error."""
    mock_websocket.send_json.side_effect = RuntimeError("Connection closed")
    attendance_manager.add_connection(1, mock_websocket)

    with patch.object(
        attendance_manager, "get_dashboard_data", return_value={"test_data": "value"}
    ):
        await attendance_manager.broadcast_update()

    mock_websocket.send_json.assert_called_once()
    # Ensure error is logged but does not break other updates


@pytest.mark.asyncio
async def test_add_and_remove_connection(attendance_manager, mock_websocket):
    """Test adding and removing WebSocket connections."""
    attendance_manager.add_connection(1, mock_websocket)
    assert 1 in attendance_manager.active_connections

    attendance_manager.remove_connection(1)
    assert 1 not in attendance_manager.active_connections


import pytest
import logging
from backend.db.models import Interaction

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_get_dashboard_data(attendance_manager):
    """Test fetching dashboard data."""
    # Crear un mock de interacción
    interaction_mock = Interaction(
        id=1,
        student_name="John Doe",
        tutor_phone="+1234567890",
        claude_response={"message": "Test response"},
        status="active",
        timestamp=datetime.now(),
    )

    # Crear una clase mock para simular el resultado de scalars()
    class MockScalarsResult:
        def all(self):
            logger.debug("MockScalarsResult.all() called")
            return [interaction_mock]

    # Crear una clase mock para simular el resultado de execute()
    class MockExecuteResult:
        def scalars(self):
            logger.debug("MockExecuteResult.scalars() called")
            return MockScalarsResult()

    # Crear el mock de la sesión
    mock_session = AsyncMock()

    # Configurar execute() para retornar nuestro resultado personalizado
    async def mock_execute(*args, **kwargs):
        logger.debug("mock_execute called")
        return MockExecuteResult()

    mock_session.execute = AsyncMock(side_effect=mock_execute)
    mock_session.close = AsyncMock()

    # Mock del context manager
    @asynccontextmanager
    async def mock_get_db():
        logger.debug("Entering mock_get_db context")
        try:
            yield mock_session
        finally:
            logger.debug("Exiting mock_get_db context")
            await mock_session.close()

    # Mock del service status
    async def mock_service_status():
        logger.debug("mock_service_status called")
        return {"claude": True, "meta": True}

    logger.debug("Starting test with patches")

    # Aplicar los patches
    with patch("backend.services.attendance.get_db", return_value=mock_get_db()):
        with patch.object(
            attendance_manager, "check_service_status", side_effect=mock_service_status
        ):
            logger.debug("Calling get_dashboard_data")
            dashboard_data = await attendance_manager.get_dashboard_data()
            logger.debug(f"Received dashboard_data: {dashboard_data}")

    # Verificaciones con logging
    logger.debug(f"Verifying dashboard_data: {dashboard_data}")
    assert (
        "interactions" in dashboard_data
    ), "interactions key missing from dashboard_data"
    assert (
        len(dashboard_data["interactions"]) == 1
    ), f"Expected 1 interaction, got {len(dashboard_data['interactions'])}"

    interaction = dashboard_data["interactions"][0]
    assert (
        interaction["student_name"] == "John Doe"
    ), f"Expected John Doe, got {interaction['student_name']}"
    assert interaction["id"] == 1, f"Expected id 1, got {interaction['id']}"
    assert (
        interaction["status"] == "active"
    ), f"Expected status active, got {interaction['status']}"

    # Verificar las llamadas a los mocks
    assert mock_session.execute.called, "execute was not called"
    assert mock_session.close.called, "close was not called"

    logger.debug("Test completed successfully")


@pytest.mark.asyncio
async def test_check_service_status():
    """Test checking the status of external services."""
    with patch("aiohttp.ClientSession.get", AsyncMock()) as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 200

        status = await AttendanceManager.check_service_status()

    assert status["claude"] is True
    assert status["meta"] is True


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_save_interaction():
    """Test saving an interaction to the database."""
    manager = AttendanceManager.get_instance()

    mock_db_session = AsyncMock()
    mock_student_name = "John Doe"
    mock_tutor_phone = "+34600111222"
    mock_claude_response = {"response": "Mock Claude Response"}

    # async def save_interaction(self, db_session, student_name: str, tutor_phone: str, claude_response: dict):

    await manager.save_interaction(
        mock_db_session, mock_student_name, mock_tutor_phone, mock_claude_response
    )

    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()


async def test_generate_claude_response_mock():
    """Prueba la generación de respuestas de Claude con un mock."""
    mock_response = {
        "content": [
            {
                "text": json.dumps(
                    {
                        "sensitivity": 7,
                        "response": "Mock response with sensitivity",
                        "likely_to_be_on_leave_tomorrow": False,
                        "reach_out_tomorrow": True,
                    }
                ),
                "type": "text",
            }
        ],
    }

    with patch(
        "backend.services.claude.ClaudeService.generate_response",
        new=AsyncMock(return_value=mock_response),
    ):
        response = await generate_claude_response("Test Student")
        assert "content" in response
        assert len(response["content"]) > 0
        assert "text" in response["content"][0]


import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_generate_claude_response_error():
    """Prueba el manejo de errores en las respuestas de Claude."""
    claude_service = ClaudeService.get_instance()

    # Crear un mock que simule el context manager
    mock_context = AsyncMock()
    mock_context.__aenter__.side_effect = Exception(
        "API Error"
    )  # Simula una excepción en el context manager
    mock_context.__aexit__ = AsyncMock()

    mock_session = AsyncMock()
    mock_session.post.return_value = mock_context

    # Hacer patch directamente de _session
    with patch.object(claude_service, "_session", mock_session):
        response = await generate_claude_response("Test Student")

        # Verificaciones del resultado
        assert response["sensitivity"] == 5  # valor por defecto
        assert "Error" in response["response"]
        # assert response["response"] == "Error: API Error"  # Verificación exacta del mensaje


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_check_service_status():
    """Prueba la verificación del estado de los servicios."""
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 200

        status = await AttendanceManager.check_service_status()
        assert isinstance(status, dict)
        assert "claude" in status
        assert "meta" in status
        assert all(isinstance(v, bool) for v in status.values())


import pytest
from backend.services.attendance import AttendanceManager


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_broadcast_update(db_session):
    """Prueba la difusión de actualizaciones."""
    # Obtener la instancia del singleton
    attendance_manager = AttendanceManager.get_instance()

    # Crear el mock del websocket
    mock_websocket = MagicMock()
    mock_websocket.send_json = AsyncMock()

    # Configurar las conexiones activas
    attendance_manager.active_connections = {1: mock_websocket}

    # Mock de get_dashboard_data para evitar llamadas reales a la base de datos
    mock_dashboard_data = {
        "service_status": {"claude": True, "meta": True},
        "interactions": [],
    }

    # Aplicar el patch para get_dashboard_data
    with patch.object(
        attendance_manager, "get_dashboard_data", return_value=mock_dashboard_data
    ):
        # Llamar al método de instancia
        await attendance_manager.broadcast_update()

    # Verificar que se llamó send_json con los datos correctos
    mock_websocket.send_json.assert_called_once_with(
        {"type": "update", "data": mock_dashboard_data}
    )

    # Opcionalmente, verificar que solo se llamó una vez
    assert mock_websocket.send_json.call_count == 1


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_phone_number_validation():
    """Prueba la validación de números de teléfono."""
    from backend.services import PhoneNumberValidator

    # Números españoles válidos
    assert PhoneNumberValidator.validate_phone("+34666777888", "ES")
    assert PhoneNumberValidator.validate_phone("+34911234567", "ES")

    # Números estadounidenses válidos
    assert PhoneNumberValidator.validate_phone("+12125551234", "US")
    assert PhoneNumberValidator.validate_phone("+19175551234", "US")

    # Números inválidos
    assert not PhoneNumberValidator.validate_phone("+1212555", "US")
    assert not PhoneNumberValidator.validate_phone("+3466677", "ES")
    assert not PhoneNumberValidator.validate_phone("invalid", "ES")


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_message_formatter():
    """Prueba el formateador de mensajes."""
    from backend.services import MessageFormatter

    # Prueba con diferentes idiomas
    es_message = MessageFormatter.get_message(
        "INITIAL_CONTACT", "es-ES", student_name="Juan", school_name="IES Test"
    )
    assert "Juan" in es_message
    assert "IES Test" in es_message

    en_message = MessageFormatter.get_message(
        "INITIAL_CONTACT", "en-US", student_name="John", school_name="Test High School"
    )
    assert "John" in en_message
    assert "Test High School" in en_message


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_error_handling():
    """Prueba el manejo de errores en los servicios."""
    claude_service = ClaudeService.get_instance()
    mock_session = AsyncMock()
    with patch.object(claude_service, "_session", new=mock_session):
        # Parchear el método post de la sesión mock
        mock_session.post.return_value.__aenter__.return_value.json.return_value = {
            "content": [
                {
                    "text": json.dumps(
                        {
                            "sensitivity": 5,
                            "response": "This is a test response.",
                            "likely_to_be_on_leave_tomorrow": False,
                            "reach_out_tomorrow": True,
                        }
                    )
                }
            ]
        }

    settings = get_settings()
    # Configuración del servicio de WhatsApp
    service = WhatsAppService(
        provider=MessageProvider.CALLMEBOT,
        meta_api_key=None,
        callback_token=settings.WHATSAPP_CALLBACK_TOKEN,
    )
    await service.init_service()
    phone = "NOT_A_VALID_PHONENUMBER"

    # Mock del cliente HTTP
    with patch(
        "aiohttp.ClientSession.get",
        side_effect=ValueError(f"Invalid phone number: {phone}"),
    ) as mock_get:
        with pytest.raises(ValueError):
            await service.send_message(phone, "Test message")
    await service.close_service()


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_service_status_updates(db_session):
    """Prueba las actualizaciones de estado de servicios."""
    try:
        # Crear un nuevo estado de servicio
        service = ServiceStatus(
            service_name="test_service", status=True, last_check=datetime.utcnow()
        )

        # Añadir la entidad a la sesión (sin await)
        db_session.add(service)
        # Commit sí es asíncrono
        await db_session.commit()

        # Actualizar el estado
        service.status = False
        service.error_message = "Test error"
        await db_session.commit()

        # Verificar la actualización
        result = await db_session.execute(
            select(ServiceStatus).filter_by(service_name="test_service")
        )
        updated_service = result.scalar_one_or_none()

        # Verificaciones
        assert updated_service is not None, "Service not found"
        assert not updated_service.status, "Status should be False"
        assert (
            updated_service.error_message == "Test error"
        ), "Error message not updated"

    except Exception as e:
        await db_session.rollback()
        raise


@pytest.fixture
def mock_claude_response():
    """Fixture para crear respuestas mock de Claude."""

    def create_response(
        sensitivity, response="Test response", leave_tomorrow=False, reach_out=True
    ):
        return json.dumps(
            {
                "sensitivity": sensitivity,
                "response": response,
                "likely_to_be_on_leave_tomorrow": leave_tomorrow,
                "reach_out_tomorrow": reach_out,
            }
        )

    return create_response


class MockResponse:
    def __init__(self, data):
        self._data = data

    async def json(self):
        return self._data


class AsyncContextManagerMock:
    def __init__(self, return_value):
        self.return_value = return_value
        self.enter_called = False
        self.exit_called = False

    async def __aenter__(self):
        self.enter_called = True
        return self.return_value

    async def __aexit__(self, exc_type, exc, tb):
        self.exit_called = True


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_interaction_sensitivity_calculation():
    with patch("aiohttp.ClientSession") as mock_session_class:
        claude_service = ClaudeService.get_instance()

        mock_response = AsyncMock()
        mock_session = mock_session_class.return_value
        mock_session.post.return_value.__aenter__.return_value.json.return_value = {
            "content": [
                {
                    "text": json.dumps(
                        {
                            "sensitivity": 7,
                            "response": "Test response",
                            "likely_to_be_on_leave_tomorrow": False,
                            "reach_out_tomorrow": True,
                        }
                    )
                }
            ]
        }

        response = await claude_service.generate_response(
            "Test Student", "El estudiante está enfermo"
        )
        assert response["sensitivity"] == 7


@pytest.fixture(autouse=True)
async def cleanup_claude_service():
    yield
    service = ClaudeService.get_instance()
    service._session = AsyncMock()
    service._session.close = AsyncMock()
    await service.close_session()


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_interaction_sensitivity_error_handling():
    claude_service = ClaudeService.get_instance()

    mock_session = AsyncMock()
    mock_session.post.side_effect = Exception("API Error")
    mock_session.close = AsyncMock()
    claude_service._session = mock_session

    response = await claude_service.generate_response("Test Student", "Test message")

    assert response["sensitivity"] == 5
    assert "Error" in response["response"]
    assert not response["likely_to_be_on_leave_tomorrow"]
    assert not response["reach_out_tomorrow"]


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_interaction_sensitivity_invalid_json():
    claude_service = ClaudeService.get_instance()

    mock_context = AsyncMock()
    mock_context.json.return_value = {"content": [{"text": "Invalid JSON response"}]}

    mock_session = AsyncMock()
    mock_session.post.return_value = mock_context
    mock_session.close = AsyncMock()
    claude_service._session = mock_session

    response = await claude_service.generate_response("Test Student", "Test message")

    assert response["sensitivity"] == 5
    assert isinstance(response["response"], str)


if __name__ == "__main__":
    pytest.main(["-v", __file__])
