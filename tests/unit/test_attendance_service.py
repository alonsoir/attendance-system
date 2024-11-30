import asyncio
import datetime
import logging
import time
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.exc import SQLAlchemyError
from starlette.websockets import WebSocket

from backend.services.attendance import OutgoingMessage, MessageData
import asyncio
import datetime
import logging
import time
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.exc import SQLAlchemyError
from starlette.websockets import WebSocket

from backend.services.attendance import OutgoingMessage, MessageData

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
    return IncomingMessage(
        sender_phone="12025550179",
        sender_name="Test Sender",
        message_content="Mi hijo está enfermo",
        timestamp=generate_whatsapp_timestamp()
    )

@pytest.fixture
def invalid_incomming_message_data():
    """Fixture que proporciona datos inválidos de mensaje."""
    return IncomingMessage(
        sender_phone="invalid_sender_phone",
        sender_name="invalid_sender_name",
        message_content="Mi hijo está enfermo",
        timestamp=generate_whatsapp_timestamp()
    )

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
def attendance_manager():
    """Fixture for providing a clean instance of AttendanceManager."""
    manager = AttendanceManager.get_instance()
    # Reset active connections for isolated tests
    manager.active_connections = {}
    return manager

from backend.services.attendance import AttendanceManager, IncomingMessage

@pytest.mark.asyncio
@pytest.mark.unittest
async def test_validate_message_data(attendance_manager, valid_incomming_message_data):
    """Prueba la validación de datos del mensaje."""
    # Convertir diccionario a IncomingMessage
    valid_message = IncomingMessage(**valid_incomming_message_data)

    # Caso válido
    result: IncomingMessage = attendance_manager._validate_incoming_message_data(valid_message)
    assert result.sender_phone == valid_message.sender_phone
    assert result.message_content == valid_message.message_content
    assert result.sender_name == valid_message.sender_name
    assert result.timestamp == valid_message.timestamp

    # Casos inválidos
    invalid_cases = [
        # Teléfono inválido
        (IncomingMessage(**{**valid_incomming_message_data, "sender_phone": "invalid"}),
         "Invalid sender_phone number format"),
        # Teléfono vacío
        (IncomingMessage(**{**valid_incomming_message_data, "sender_phone": ""}),
         "sender_phone is required"),
        # Nombre vacío
        (IncomingMessage(**{**valid_incomming_message_data, "sender_name": ""}),
         "sender_name is required"),
        # Mensaje vacío
        (IncomingMessage(**{**valid_incomming_message_data, "message_content": ""}),
         "message_content is required"),
        # Timestamp inválido
        (IncomingMessage(**{**valid_incomming_message_data, "timestamp": -1}),
         "timestamp is invalid or required"),
    ]

    for invalid_message, expected_error in invalid_cases:
        with pytest.raises(ValueError) as exc_info:
            attendance_manager._validate_incoming_message_data(invalid_message)
        assert expected_error in str(exc_info.value)

"""
@pytest.mark.asyncio
@pytest.mark.unittest
async def test_validate_message_data_missing_fields(attendance_manager,invalid_incomming_message_data):
    with pytest.raises(ValueError) as exc_info:
        attendance_manager._validate_message_data(invalid_incomming_message_data)
    assert "student_name is required" in str(exc_info.value)
"""

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


from datetime import datetime

"""
@pytest.mark.asyncio
@pytest.mark.unittest
async def test_message_data_conversion(attendance_manager, valid_message_data):
    message_data = attendance_manager._validate_message_data(valid_message_data)
    dict_data = message_data.to_dict()

    assert isinstance(dict_data, dict)
    assert dict_data["student_name"] == valid_message_data["student_name"]
    assert dict_data["tutor_phone"] == valid_message_data["tutor_phone"]
    assert isinstance(dict_data["timestamp"], datetime)
"""
import pytest


@pytest.fixture
def mock_send_whatsapp():
    with patch("backend.services.whatsapp.WhatsAppService.send_message") as mock:
        yield mock

import pytest
from unittest.mock import patch

@pytest.fixture
def mock_process_whatsapp_message_from_tutor_to_claude():
    with patch("backend.services.attendance.AttendanceManager.process_whatsapp_message_from_tutor_to_claude") as mock:
        yield mock

@pytest.fixture
def mock_process_whatsapp_message_from_college_to_tutor():
    with patch("backend.services.attendance.AttendanceManager.process_whatsapp_message_from_college_to_tutor") as mock:
        yield mock

@pytest.fixture
def mock_validate_phone_number():
    with patch("backend.services.attendance.AttendanceManager.validate_phone_number") as mock:
        yield mock
@pytest.fixture
def mock_validate_outgoing_message_data():
    with patch("backend.services.attendance.AttendanceManager._validate_outgoing_message_data") as mock:
        yield mock

@pytest.fixture
def attendance_manager():
    """Fixture for providing a clean instance of AttendanceManager."""
    manager = AttendanceManager.get_instance()
    # Reset active connections for isolated tests
    manager.active_connections = {}
    return manager

@pytest.mark.asyncio
@pytest.mark.unittest
async def test_attendance_manager_send_response_error(
    attendance_manager, mock_process_whatsapp_message_from_tutor_to_claude
):
    """Prueba el envío de respuesta cuando hay un error."""
    mock_process_whatsapp_message_from_tutor_to_claude.side_effect = Exception("Network error")
    message_from_tutor = IncomingMessage(
        sender_phone="+12025550179",
        sender_name="Alonso",
        message_content="Hello, i am the tutor, my name is Alonso!",
        timestamp=int(time.time())
    )
    with pytest.raises(Exception) as exc:
        await attendance_manager.process_whatsapp_message_from_tutor_to_claude(
            message_from_tutor
        )

    assert "Network error" in str(exc.value)
    mock_process_whatsapp_message_from_tutor_to_claude.assert_called_once_with(message_from_tutor)

@pytest.mark.asyncio
async def test_attendance_manager_process_whatsapp_message_from_college_to_tutor(
        attendance_manager
):
    """Prueba el procesamiento de mensaje en AttendanceManager._process_whatsapp_message_from_college_to_tutor"""
    message_data = OutgoingMessage(
        messaging_product="whatsapp",
        to="+12025550179",
        type="text",
        body="Hello, i am the tutor, my name is Alonso!",
    )

    mock_response = MessageData(
        id=None,
        student_name="Estudiante",
        tutor_phone=message_data.to,
        college_phone="college_phone",
        college_name="College Name",
        message_content=message_data.body,
        tutor_name="Tutor",
        timestamp=datetime.now()
    )

    # Mock el método que realmente hace el envío
    with patch.object(
            attendance_manager,
            '_send_message_to_tutor',
            return_value=mock_response
    ) as mock_send:
        # Mock el método de guardado en DB
        with patch.object(
                attendance_manager,
                '_save_interaction_to_db',
                return_value=None
        ) as mock_save:
            result = await attendance_manager.process_whatsapp_message_from_college_to_tutor(message_data)

            # Verificar el resultado
            assert result["status"] == "success"
            assert result["response"] == "Message processed successfully"

            # Verificar que se llamaron los métodos correctos
            mock_send.assert_called_once()
            mock_save.assert_called_once_with(mock_response)

            # Verificar el formato de los datos
            assert isinstance(message_data.messaging_product, str)
            assert message_data.messaging_product == "whatsapp"
            assert isinstance(message_data.body, str)
            assert message_data.body == "Hello, i am the tutor, my name is Alonso!"

@pytest.mark.asyncio
async def test_attendance_manager_process_whatsapp_message_from_college_to_tutor_invalid_data(
    attendance_manager
):
    """Prueba el procesamiento de mensaje con datos inválidos."""
    # Preparar los datos de prueba
    message_data = OutgoingMessage(
        messaging_product="whatsapp",
        to="111112025550179",  # Invalid phone number
        type="text",
        body="Hello, i am the tutor, my name is Alonso!",
    )

    # No necesitamos mockear la validación porque ya está implementada
    result = await attendance_manager.process_whatsapp_message_from_college_to_tutor(
        message_data
    )

    # Verificar que se maneja el error correctamente
    assert result["status"] == "error"
    assert "Processing failed" in result["message"]
    assert result["error_type"] == "ValueError"


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_process_whatsapp_message_from_college_to_tutor_message(
        mock_whatsapp_message, attendance_manager
):
    """Test processing of WhatsApp messages via AttendanceManager."""
    # Crear el mensaje de prueba usando OutgoingMessage
    mock_message = OutgoingMessage(
        messaging_product="whatsapp",
        to="+34600111222",  # tutor_phone
        type="text",
        body=f"Consulta sobre el estudiante John Doe"
    )

    expected_response = MessageData(
        id=None,
        student_name="John Doe",
        tutor_phone="+34600111222",
        college_phone="college_phone",
        college_name="College Name",
        message_content="Test response",
        tutor_name="Tutor",
        timestamp=datetime.now()
    )

    # Mockear los métodos que se usan internamente
    with patch.object(
            attendance_manager,
            '_send_message_to_tutor',
            AsyncMock(return_value=expected_response)
    ) as mock_send:
        with patch.object(
                attendance_manager,
                '_save_interaction_to_db',
                AsyncMock()
        ) as mock_save:
            result = await attendance_manager.process_whatsapp_message_from_college_to_tutor(mock_message)

            # Verificaciones
            assert result["status"] == "success"
            assert result["response"] == "Message processed successfully"

            # Verificar que se llamaron los métodos internos
            mock_send.assert_called_once()
            mock_save.assert_called_once_with(expected_response)

            # Verificar que los datos del mensaje son correctos
            sent_message = mock_send.call_args[0][0]
            assert isinstance(sent_message, MessageData)
            assert sent_message.tutor_phone == "+34600111222"

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
    outgoing_message = OutgoingMessage(
        messaging_product="whatsapp",
        to="+12025550179",  # Formato correcto con '+' y longitud adecuada
        type="text",
        body="Hello, i am the tutor, my name is Alonso!",
    )

    expected_response = MessageData(
        id=None,
        student_name="Estudiante",
        tutor_phone="+12025550179",  # Mantener consistencia con el número de arriba
        college_phone="college_phone",
        college_name="College Name",
        message_content="Hello, i am the tutor, my name is Alonso!",
        tutor_name="Tutor",
        timestamp=datetime.now()
    )

    # Mockear los métodos internos que realmente se usan
    with patch.object(
            attendance_manager,
            '_send_message_to_tutor',
            AsyncMock(return_value=expected_response)
    ) as mock_send:
        with patch.object(
                attendance_manager,
                '_save_interaction_to_db',
                AsyncMock()
        ) as mock_save:
            response = await attendance_manager.process_whatsapp_message_from_college_to_tutor(
                outgoing_message
            )

            # Verificar la respuesta
            assert response["status"] == "success"
            assert response["response"] == "Message processed successfully"

            # Verificar que se llamaron los métodos internos
            mock_send.assert_called_once()
            mock_save.assert_called_once_with(expected_response)

            # Verificar que los datos pasados son correctos
            sent_message = mock_send.call_args[0][0]
            assert isinstance(sent_message, MessageData)
            assert sent_message.tutor_phone == "+12025550179"
            assert sent_message.message_content == "Hello, i am the tutor, my name is Alonso!"


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
@pytest.mark.unittest
async def test_process_whatsapp_message_from_college_to_tutor_message_exception(
        attendance_manager,
):
    """Test handling an unexpected API error."""
    # Usar un número de teléfono en formato válido
    outgoing_message = OutgoingMessage(
        messaging_product="whatsapp",
        to="+12025550179",  # Formato válido de número de teléfono
        type="text",
        body="Test message"
    )

    # Mock el método que lanza la excepción
    with patch.object(
            attendance_manager,
            '_send_message_to_tutor',
            AsyncMock(side_effect=Exception("API error"))
    ) as mock_send:
        with patch.object(
                attendance_manager,
                '_validate_outgoing_message_data',
                # Mock la validación para que pase sin problemas
                return_value=outgoing_message
        ):
            response = await attendance_manager.process_whatsapp_message_from_college_to_tutor(
                outgoing_message
            )

            # Verificar la respuesta de error
            assert response["status"] == "error"
            assert "API error" in response["message"]
            assert response["error_type"] == "Exception"

            # Verificar que se intentó enviar el mensaje
            mock_send.assert_called_once()


@pytest.mark.asyncio
async def test_process_whatsapp_message_from_college_to_tutor_incomplete_data(
        attendance_manager,
):
    """Test WhatsApp message processing with missing required fields."""
    # Crear un mensaje incompleto usando OutgoingMessage
    outgoing_message = OutgoingMessage(
        messaging_product="",  # Campo requerido vacío
        to="",  # Campo requerido vacío
        type="",  # Campo requerido vacío
        body=""  # Campo requerido vacío
    )

    # Obtener la respuesta del método
    response = await attendance_manager.process_whatsapp_message_from_college_to_tutor(
        outgoing_message
    )

    # Verificar que la respuesta indica error
    assert response["status"] == "error"
    assert response["error_type"] == "ValueError"
    assert "Processing failed" in response["message"]

    # Verificar que el mensaje incluye todos los errores de validación
    error_message = response["message"]
    assert "messaging_product is required" in error_message
    assert "to is required" in error_message
    assert "type is required" in error_message
    assert "body is required" in error_message

    # Test con teléfono inválido
    outgoing_message = OutgoingMessage(
        messaging_product="whatsapp",
        to="invalid_phone",
        type="text",
        body="test message"
    )

    response = await attendance_manager.process_whatsapp_message_from_college_to_tutor(
        outgoing_message
    )

    # Verificar respuesta para teléfono inválido
    assert response["status"] == "error"
    assert response["error_type"] == "ValueError"
    assert "Processing failed" in response["message"]
    assert "to is invalid" in response["message"]

@pytest.mark.asyncio
async def test_process_whatsapp_message_from_college_to_tutor_db_error(
    attendance_manager,
):
    """Test WhatsApp message processing with a database error."""
    outgoing_message = OutgoingMessage(
        messaging_product="whatsapp",
        to="+12025550179",  # Número válido
        type="text",
        body="Test message"
    )

    # Simular error de DB en _save_interaction_to_db
    with patch.object(
        attendance_manager,
        '_save_interaction_to_db',
        AsyncMock(side_effect=SQLAlchemyError("DB Error"))
    ) as mock_save:
        # Mock el método de envío para que no falle
        with patch.object(
            attendance_manager,
            '_send_message_to_tutor',
            AsyncMock(return_value=MessageData(
                id=None,
                student_name="Test Student",
                tutor_phone="+12025550179",
                college_phone="college_phone",
                college_name="College Name",
                message_content="Test message",
                tutor_name="Tutor",
                timestamp=datetime.now()
            ))
        ):
            response = await attendance_manager.process_whatsapp_message_from_college_to_tutor(
                outgoing_message
            )

            # Verificar la respuesta de error
            assert response["status"] == "error"
            assert "DB Error" in response["message"]
            assert response["error_type"] == "SQLAlchemyError"

            # Verificar que se intentó guardar en la DB
            mock_save.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_edge_cases(attendance_manager):
    """Test edge cases in data handling."""
    test_cases = [
        (
            OutgoingMessage(
                messaging_product="whatsapp",
                to="+1234567890",
                type="text",
                body=""
            ),
            "body is required"
        ),
        (
            OutgoingMessage(
                messaging_product="whatsapp",
                to="+1234567890",
                type="",  # tipo vacío
                body="Test message"
            ),
            "type is required"
        ),
        (
            OutgoingMessage(
                messaging_product="whatsapp",
                to="+1",  # teléfono inválido
                type="text",
                body="Test message"
            ),
            "to is invalid"
        ),
        (
            OutgoingMessage(
                messaging_product="",  # messaging_product requerido
                to="+1234567890",
                type="text",
                body="Test message"
            ),
            "messaging_product is required"
        ),
    ]

    for outgoing_message, expected_error in test_cases:
        logger.debug(f"Testing case: {outgoing_message} expecting error: {expected_error}")
        response = await attendance_manager.process_whatsapp_message_from_college_to_tutor(
            outgoing_message
        )

        # Verificar que la respuesta indica error
        assert response["status"] == "error"
        assert expected_error in response["message"]
        assert response["error_type"] == "ValueError"

    # Verificación opcional
    assert not attendance_manager.active_connections, "No deberían quedar conexiones activas"