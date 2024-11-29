import asyncio
import datetime
import logging
import time
from contextlib import asynccontextmanager
from unittest.mock import patch, AsyncMock

import pytest
from sqlalchemy.exc import SQLAlchemyError
from starlette.websockets import WebSocket

from backend.services import AttendanceManager
from backend.services.attendance import IncomingMessage

logger = logging.getLogger(__name__)


import random


def generate_whatsapp_timestamp() -> int:
    """
    Genera un timestamp en formato Unix epoch como el que envía WhatsApp.

    Returns:
        int: Timestamp en segundos desde el epoch (UTC).
    """
    return int(time.time())
def generar_id_unico():
    """Genera un número entero aleatorio que simula un ID único para una base de datos."""
    return random.randint(1, 10**9)  # Número aleatorio entre 1 y 1,000,000,000

@pytest.fixture
def valid_incomming_message_data():
    """Fixture que proporciona datos válidos de mensaje."""
    return {
        "sender_phone": "12025550179",
        "sender_name": "Test Sender",
        "message_content": "Mi hijo está enfermo",
        "timestamp": generate_whatsapp_timestamp()
    }

@pytest.fixture
def invalid_incomming_message_data():
    """Fixture que proporciona datos válidos de mensaje."""
    return {
        "sender_phone": "invalid_sender_phone",
        "sender_name": "invalid_sender_name",
        "message_content": "Mi hijo está enfermo",
        "timestamp": generate_whatsapp_timestamp()
    }

@pytest.fixture
def valid_message_data():
    """Fixture que proporciona datos válidos de mensaje."""
    return {
        "id": generar_id_unico(),
        "student_name": "Test Student",
        "tutor_phone": "+34666777888",
        "college_phone": "+34916777888",
        "college_name": "Test College name",
        "message_content": "El estudiante está enfermo",
        "tutor_name": "Test Parent",
    }


@pytest.fixture
def invalid_message_data():
    """Fixture que proporciona datos válidos de mensaje."""
    return {
        "id": generar_id_unico(),
        "student_name": "Test Student",
        "tutor_phone": "invalid_tutor_phone",
        "college_phone": "invalid_college_phone",
        "college_name": "invalid_Test College name",
        "message_content": "El estudiante está enfermo",
        "tutor_name": "Test Parent",
    }

@pytest.mark.asyncio
@pytest.mark.unittest
async def test_validate_phone_number(attendance_manager):
    """Prueba la validación de números de teléfono de España y Estados Unidos."""
    valid_phones = [
        # Números de España
        "34666777888",  # España móvil sin +, formato WhatsApp
        "+34666777888",  # España móvil con +
        "34916777888",  # España fijo sin +, formato WhatsApp
        "+34916777888",  # España fijo con +
        "34722777888",  # España móvil empezando con 7
        "+34822777888",  # España móvil empezando con 8
        "+34922777888",  # España fijo empezando con 9

        # Números de Estados Unidos
        "12025550179",  # USA DC sin +
        "+12025550179",  # USA DC con +
        "14155552671",  # USA CA sin +
        "+14155552671",  # USA CA con +
    ]

    invalid_phones = [
        # Casos vacíos o inválidos
        "",
        "abc123",
        "+",
        "12",

        # Números mal formados
        "+34ABC123456",  # Caracteres inválidos
        "666777888",  # España: falta código país
        "5551234567",  # USA: falta código país

        # Números de países no soportados
        "+441234567890",  # UK
        "+33123456789",  # Francia
        "+491234567890",  # Alemania

        # Números con formato incorrecto
        "+34555555555",  # España: no empieza por 6,7,8,9
        "+1123",  # USA: muy corto
        "+1123456789",  # USA: falta un dígito
        "+11234567890123",  # USA: demasiado largo
        "1234567890",  # USA: falta código país
        "+1",  # USA: solo código país
        "34",  # España: solo código país
    ]

    # Prueba números válidos
    for phone in valid_phones:
        print(f"Testing valid phone: {phone}")
        is_valid = attendance_manager._validate_phone_number(phone)
        assert is_valid, f"Should be valid: {phone}"

    # Prueba números inválidos
    for phone in invalid_phones:
        print(f"Testing invalid phone: {phone}")
        is_valid = attendance_manager._validate_phone_number(phone)
        assert not is_valid, f"Should be invalid: {phone}"


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_validate_message_data(attendance_manager, valid_incomming_message_data):
    """Prueba la validación de datos del mensaje."""
    # Caso válido
    result = attendance_manager._validate_incoming_message_data(valid_incomming_message_data)
    assert result is True, "Should be valid"

    # Casos inválidos
    invalid_cases = [
        # Teléfono inválido
        ({**valid_incomming_message_data, "sender_phone": "invalid"}, "Invalid sender_phone number format"),
        # Teléfono vacío
        ({**valid_incomming_message_data, "sender_phone": ""}, "sender_phone is required"),
        # Nombre vacío
        ({**valid_incomming_message_data, "sender_name": ""}, "sender_name is required"),
        # Mensaje vacío
        ({**valid_incomming_message_data, "message_content": ""}, "message_content is required"),
        # Timestamp inválido
        ({**valid_incomming_message_data, "timestamp": -1}, "timestamp is invalid or required"),
    ]

    for invalid_data, expected_error in invalid_cases:
        with pytest.raises(ValueError) as exc_info:
            attendance_manager._validate_incoming_message_data(invalid_data)
        assert expected_error in str(exc_info.value)


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_validate_message_data_missing_fields(attendance_manager,invalid_incomming_message_data):
    """Prueba la validación con campos faltantes."""
    invalid_data = {"message_content": "Test message"}

    with pytest.raises(ValueError) as exc_info:
        attendance_manager._validate_message_data(invalid_incomming_message_data)
    assert "student_name is required" in str(exc_info.value)


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_process_whatsapp_message_from_tutor_to_claude_success(
    attendance_manager, valid_incomming_message_data
):
    """Prueba el procesamiento exitoso de un mensaje."""
    mock_callback = AsyncMock()

    with patch(
        "backend.services.attendance.AttendanceManager.process_whatsapp_message_from_tutor_to_claude"
    ) as mock_process:
        mock_process.return_value = {
            "status": "success",
            "response": "Message processed successfully",
        }

        result = await attendance_manager.process_whatsapp_message_from_tutor_to_claude(
            valid_incomming_message_data, mock_callback
        )

        assert result["status"] == "success"
        assert "Message processed successfully" in result["response"]


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_process_whatsapp_message_from_tutor_to_claude_validation_error(
    attendance_manager, invalid_incomming_message_data
):
    """Prueba el manejo de errores de validación."""
    with pytest.raises(ValueError) as exc_info:
        await attendance_manager.process_whatsapp_message_from_tutor_to_claude(
            invalid_incomming_message_data
        )
    assert "Validation failed" in str(exc_info.value)

@pytest.mark.asyncio
@pytest.mark.unittest
async def test_concurrent_process_whatsapp_message_from_tutor_to_claude(
    attendance_manager, valid_incomming_message_data
):
    # Procesar múltiples mensajes concurrentemente
    tasks = [
        attendance_manager.process_whatsapp_message_from_tutor_to_claude(
            IncomingMessage(**valid_incomming_message_data.copy())
        )
        for _ in range(5)
    ]
    results = await asyncio.gather(*tasks)

    assert all(result["status"] == "success" for result in results)

@pytest.mark.asyncio
@pytest.mark.unittest
async def test_message_data_conversion(attendance_manager, valid_message_data):
    """Prueba la conversión de datos del mensaje."""
    message_data = attendance_manager._validate_message_data(valid_message_data)
    dict_data = message_data.to_dict()

    assert isinstance(dict_data, dict)
    assert dict_data["student_name"] == valid_message_data["student_name"]
    assert dict_data["tutor_phone"] == valid_message_data["tutor_phone"]
    assert isinstance(dict_data["timestamp"], datetime)


@patch("backend.services.whatsapp.WhatsAppService.send_message")
async def test_attendance_manager_send_response_error(
    attendance_manager, mock_send_whatsapp
):
    """Prueba el envío de respuesta cuando hay un error."""
    mock_send_whatsapp.side_effect = Exception("Network error")
    message_from_tutor = "Hello, i am the tutor, my name is Alonso!"
    with pytest.raises(Exception) as exc:
        await attendance_manager.process_whatsapp_message_from_tutor_to_claude(
            message_data=message_from_tutor
        )

    assert "Error sending response" in str(exc.value)
    mock_send_whatsapp.assert_called_once_with(message_from_tutor)

    assert "Network error" in str(exc.value)
    mock_send_whatsapp.assert_called_once_with(message_from_tutor)


@pytest.mark.asyncio
@patch("backend.services.attendance.AttendanceManager._validate_phone_number")
@patch("backend.services.attendance.AttendanceManager.process_whatsapp_message")
async def test_attendance_manager_process_message(
    attendance_manager, mock_process_whatsapp, mock_validate_phone
):
    """Prueba el procesamiento de mensaje en MessageCoordinator."""
    mock_validate_phone.side_effect = [True, True]
    mock_process_whatsapp.return_value = {
        "status": "success",
        "response": "Mensaje procesado",
    }

    message_data = {
        "student_name": "John Doe",
        "tutor_phone": "+34612345678",
        "college_phone": "+34987654321",
        "message_content": "Hello, world!",
    }
    result = await attendance_manager.process_whatsapp_message_from_college_to_tutor(
        message_data
    )
    assert result["status"] == "success"
    assert result["response"] == "Mensaje procesado"
    mock_validate_phone.assert_any_call(message_data["tutor_phone"])
    mock_validate_phone.assert_any_call(message_data["college_phone"])
    mock_process_whatsapp.assert_called_once_with(message_data)


@patch("backend.services.attendance.AttendanceManager._validate_phone_number")
async def test_attendance_manager_invalid_tutor_phone(
    attendance_manager, mock_validate_phone
):
    """Prueba el procesamiento de mensaje con número de teléfono inválido."""
    mock_validate_phone.side_effect = [False, True]

    message_data = {
        "student_name": "John Doe",
        "tutor_phone": "invalid_phone",
        "college_phone": "+34987654321",
        "message_content": "Hello, world!",
    }
    with pytest.raises(ValueError) as exc:
        await attendance_manager.process_whatsapp_message_from_college_to_tutor(
            message_data
        )

    assert "Invalid tutor phone number format" in str(exc.value)
    mock_validate_phone.assert_any_call(message_data["tutor_phone"])
    mock_validate_phone.assert_any_call(message_data["college_phone"])


@patch("backend.services.attendance.AttendanceManager._validate_message_data")
async def test_attendance_manager_process_whatsapp_message_from_college_to_tutor_invalid_data(
    attendance_manager, mock_validate_data
):
    """Prueba el procesamiento de mensaje con datos inválidos."""
    mock_validate_data.side_effect = ValueError("student_name is required")

    message_data = {
        "tutor_phone": "+34612345678",
        "college_phone": "+34987654321",
        "message_content": "Hello, world!",
    }
    result = await attendance_manager.process_whatsapp_message_from_college_to_tutor(
        message_data
    )

    assert result["status"] == "error"
    assert "student_name is required" in result["message"]
    mock_validate_data.assert_called_once_with(message_data)


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_process_whatsapp_message_from_college_to_tutor_message(
    mock_whatsapp_message, attendance_manager
):
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
        result = (
            await attendance_manager.process_whatsapp_message_from_college_to_tutor(
                mock_message
            )
        )
        assert result["status"] == "success"
        assert "response" in result
        assert result["response"]["response"] == "Test response"


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_verify_authorization(attendance_manager):
    """Prueba la verificación de autorización."""
    result = await attendance_manager.verify_authorization(
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
async def test_process_whatsapp_message_from_college_to_tutor_success(
    attendance_manager, mock_db_session, mock_claude_response
):
    """Test successful processing of a WhatsApp message."""
    message_data = {"student_name": "John Doe", "tutor_phone": "+1234567890"}

    with patch("backend.services.attendance.get_db", return_value=mock_db_session):
        response = (
            await attendance_manager.process_whatsapp_message_from_college_to_tutor(
                message_data
            )
        )

    # Assertions
    assert response["status"] == "success"
    assert "response" in response


@pytest.mark.asyncio
async def test_process_whatsapp_message_from_college_to_tutor_incomplete_data(
    attendance_manager,
):
    """Test processing a WhatsApp message with incomplete data."""
    incomplete_message_data = {"student_name": "John Doe"}  # Missing tutor_phone

    response = await attendance_manager.process_whatsapp_message_from_college_to_tutor(
        incomplete_message_data
    )

    assert response["status"] == "error"
    assert "Incomplete data" in response["message"]


@pytest.mark.asyncio
@patch(
    "backend.services.attendance.AttendanceManager.verify_authorization",
    AsyncMock(return_value=False),
)
async def test_process_whatsapp_message_from_college_to_tutor_message_unauthorized(
    attendance_manager,
):
    """Test unauthorized access when processing a WhatsApp message."""
    message_data = {"student_name": "John Doe", "tutor_phone": "+1234567890"}

    response = await attendance_manager.process_whatsapp_message_from_college_to_tutor(
        message_data
    )

    assert response["status"] == "error"
    assert "Unauthorized access" in response["message"]


@pytest.mark.asyncio
@patch(
    "backend.services.attendance.generate_claude_response",
    AsyncMock(side_effect=Exception("API error")),
)
async def test_process_whatsapp_message_from_college_to_tutor_message_exception(
    attendance_manager,
):
    """Test handling an unexpected exception."""
    message_data = {"student_name": "John Doe", "tutor_phone": "+1234567890"}

    response = await attendance_manager.process_whatsapp_message_from_college_to_tutor(
        message_data
    )

    assert response["status"] == "error"
    assert "API error" in response["message"]


@pytest.mark.asyncio
async def test_process_whatsapp_message_from_college_to_tutor_incomplete_data(
    attendance_manager,
):
    """Test WhatsApp message processing with missing data."""
    message_data = {"student_name": "John Doe"}  # Missing tutor_phone

    with pytest.raises(ValueError) as exc_info:
        await attendance_manager.process_whatsapp_message_from_college_to_tutor(
            message_data
        )

    assert str(exc_info.value) == "invalid_phone"


@pytest.mark.asyncio
async def test_process_whatsapp_message_from_college_to_tutor_db_error(
    attendance_manager,
):
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
                response = await attendance_manager.process_whatsapp_message_from_college_to_tutor(
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
            await attendance_manager.process_whatsapp_message_from_college_to_tutor(
                data
            )
        logger.debug(f"Received expected error: {str(exc_info.value)}")

    # Verificación opcional
    assert (
        not attendance_manager.active_connections
    ), "No deberían quedar conexiones activas"
