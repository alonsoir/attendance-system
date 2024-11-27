import asyncio
from datetime import datetime
from unittest.mock import patch, AsyncMock

import pytest

from backend.services.message_coordinator import MessageCoordinator
from backend.services.message_coordinator import MessageData


@pytest.fixture
async def coordinator():
    """Fixture que proporciona una instancia limpia de MessageCoordinator."""
    coordinator = MessageCoordinator.get_instance()
    yield coordinator
    await coordinator.cleanup()


@pytest.fixture
def valid_message_data():
    """Fixture que proporciona datos válidos de mensaje."""
    return {
        "student_name": "Test Student",
        "tutor_phone": "+34666777888",
        "message_content": "El estudiante está enfermo",
        "tutor_name": "Test Parent",
    }


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_singleton_pattern():
    """Prueba que MessageCoordinator implementa correctamente el patrón Singleton."""
    coordinator1 = MessageCoordinator.get_instance()
    coordinator2 = MessageCoordinator.get_instance()
    assert coordinator1 is coordinator2


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_validate_phone_number(coordinator):
    """Prueba la validación de números de teléfono de España y Estados Unidos."""
    valid_phones = [
        "+34666777888",  # España móvil
        "+34916777888",  # España fijo
        "+12025550179",  # USA
        "+14155552671",  # USA
    ]
    invalid_phones = [
        "",
        "abc123",
        "+",
        "12",
        "+34ABC123456",
        "666777888",  # Falta código país
        "+441234567890",  # UK no soportado
        "+34555555555",  # España: no empieza por 6,7,8,9
        "+1123",  # USA: menos de 10 dígitos
        "+1123456789012",  # USA: más de 10 dígitos
    ]

    for phone in valid_phones:
        assert coordinator._validate_phone_number(phone), f"Should be valid: {phone}"

    for phone in invalid_phones:
        assert not coordinator._validate_phone_number(
            phone
        ), f"Should be invalid: {phone}"


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_validate_message_data(coordinator, valid_message_data):
    """Prueba la validación de datos del mensaje."""
    # Caso válido
    result = coordinator._validate_message_data(valid_message_data)
    assert isinstance(result, MessageData)
    assert result.student_name == valid_message_data["student_name"]
    assert result.tutor_phone == valid_message_data["tutor_phone"]

    # Caso inválido: teléfono con formato incorrecto
    invalid_data = valid_message_data.copy()
    invalid_data["tutor_phone"] = "tutor_phone"

    with pytest.raises(ValueError) as exc_info:
        coordinator._validate_message_data(invalid_data)
    assert "Invalid phone number format" in str(exc_info.value)


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_validate_message_data_missing_fields(coordinator):
    """Prueba la validación con campos faltantes."""
    invalid_data = {"message_content": "Test message"}

    with pytest.raises(ValueError) as exc_info:
        coordinator._validate_message_data(invalid_data)
    assert "student_name is required" in str(exc_info.value)


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_process_message_success(coordinator, valid_message_data):
    """Prueba el procesamiento exitoso de un mensaje."""
    mock_callback = AsyncMock()

    with patch(
        "backend.services.attendance.AttendanceManager.process_whatsapp_message"
    ) as mock_process:
        mock_process.return_value = {
            "status": "success",
            "response": "Message processed successfully",
        }

        result = await coordinator.process_message(valid_message_data, mock_callback)

        assert result["status"] == "success"
        assert "timestamp" in result
        assert result["processing_completed"] is True
        mock_callback.assert_called_once_with(
            valid_message_data["tutor_phone"], "Message processed successfully"
        )


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_process_message_validation_error(coordinator):
    """Prueba el manejo de errores de validación."""
    invalid_data = {"student_name": "", "tutor_phone": "invalid_phone"}  # Nombre vacío
    mock_callback = AsyncMock()

    result = await coordinator.process_message(invalid_data, mock_callback)

    assert result["status"] == "error"
    assert "Validation failed" in result["message"]
    assert not mock_callback.called


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_process_message_callback_error(coordinator, valid_message_data):
    """Prueba el manejo de errores en el callback de respuesta."""
    mock_callback = AsyncMock(side_effect=Exception("Network error"))

    with patch(
        "backend.services.attendance.AttendanceManager.process_whatsapp_message"
    ) as mock_process:
        mock_process.return_value = {"status": "success", "response": "Test response"}

        result = await coordinator.process_message(valid_message_data, mock_callback)

        assert result["status"] == "success"
        assert "warning" in result
        assert "response delivery failed" in result["warning"]


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_process_message_attendance_error(coordinator, valid_message_data):
    """Prueba el manejo de errores del AttendanceManager."""
    mock_callback = AsyncMock()

    with patch(
        "backend.services.attendance.AttendanceManager.process_whatsapp_message"
    ) as mock_process:
        mock_process.side_effect = Exception("Processing error")

        result = await coordinator.process_message(valid_message_data, mock_callback)

        assert result["status"] == "error"
        assert "Processing failed" in result["message"]
        assert not mock_callback.called


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_concurrent_message_processing(coordinator, valid_message_data):
    """Prueba el procesamiento concurrente de mensajes."""
    mock_callback = AsyncMock()

    with patch(
        "backend.services.attendance.AttendanceManager.process_whatsapp_message"
    ) as mock_process:
        mock_process.return_value = {"status": "success", "response": "Test response"}

        # Procesar múltiples mensajes concurrentemente
        tasks = [
            coordinator.process_message(valid_message_data.copy(), mock_callback)
            for _ in range(5)
        ]
        results = await asyncio.gather(*tasks)

        assert all(result["status"] == "success" for result in results)
        assert mock_callback.call_count == 5


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_message_data_conversion(coordinator, valid_message_data):
    """Prueba la conversión de datos del mensaje."""
    message_data = coordinator._validate_message_data(valid_message_data)
    dict_data = message_data.to_dict()

    assert isinstance(dict_data, dict)
    assert dict_data["student_name"] == valid_message_data["student_name"]
    assert dict_data["tutor_phone"] == valid_message_data["tutor_phone"]
    assert isinstance(dict_data["timestamp"], datetime)


@patch("backend.services.whatsapp.WhatsAppService.send_message")
async def test_message_coordinator_send_response(mock_send_whatsapp):
    """Prueba el envío de respuesta en MessageCoordinator."""
    mock_send_whatsapp.return_value = {"status": "success"}

    message_coordinator = MessageCoordinator.get_instance()
    await message_coordinator.send_response("+34612345678", "Hello, tutor!")

    mock_send_whatsapp.assert_called_once_with("+34612345678", "Hello, tutor!")


@patch("backend.services.whatsapp.WhatsAppService.send_message")
async def test_message_coordinator_send_response_error(mock_send_whatsapp):
    """Prueba el envío de respuesta cuando hay un error."""
    mock_send_whatsapp.side_effect = Exception("Network error")

    message_coordinator = MessageCoordinator.get_instance()
    with pytest.raises(Exception) as exc:
        await message_coordinator.send_response("+34612345678", "Hello, tutor!")

    assert "Error sending response" in str(exc.value)
    mock_send_whatsapp.assert_called_once_with("+34612345678", "Hello, tutor!")

    assert "Network error" in str(exc.value)
    mock_send_whatsapp.assert_called_once_with("+34612345678", "Hello, tutor!")


@pytest.mark.asyncio
@patch("backend.services.message_coordinator.MessageCoordinator._validate_phone_number")
@patch("backend.services.attendance.AttendanceManager.process_whatsapp_message")
async def test_message_coordinator_process_message(
    mock_process_whatsapp, mock_validate_phone
):
    """Prueba el procesamiento de mensaje en MessageCoordinator."""
    mock_validate_phone.side_effect = [True, True]
    mock_process_whatsapp.return_value = {
        "status": "success",
        "response": "Mensaje procesado",
    }

    message_coordinator = MessageCoordinator.get_instance()
    message_data = {
        "student_name": "John Doe",
        "tutor_phone": "+34612345678",
        "college_phone": "+34987654321",
        "message_content": "Hello, world!",
    }
    result = await message_coordinator.process_message(
        message_data, message_coordinator.send_response
    )
    assert result["status"] == "success"
    assert result["response"] == "Mensaje procesado"
    mock_validate_phone.assert_any_call(message_data["tutor_phone"])
    mock_validate_phone.assert_any_call(message_data["college_phone"])
    mock_process_whatsapp.assert_called_once_with(message_data)


@patch("backend.services.message_coordinator.MessageCoordinator._validate_phone_number")
async def test_message_coordinator_invalid_phone(mock_validate_phone):
    """Prueba el procesamiento de mensaje con número de teléfono inválido."""
    mock_validate_phone.side_effect = [False, True]

    message_coordinator = MessageCoordinator.get_instance()
    message_data = {
        "student_name": "John Doe",
        "tutor_phone": "invalid_phone",
        "college_phone": "+34987654321",
        "message_content": "Hello, world!",
    }
    with pytest.raises(ValueError) as exc:
        await message_coordinator.process_message(
            message_data, message_coordinator.send_response
        )
    assert "Invalid tutor phone number format" in str(exc.value)
    mock_validate_phone.assert_any_call(message_data["tutor_phone"])
    mock_validate_phone.assert_any_call(message_data["college_phone"])


@patch("backend.services.message_coordinator.MessageCoordinator._validate_message_data")
async def test_message_coordinator_invalid_data(mock_validate_data):
    """Prueba el procesamiento de mensaje con datos inválidos."""
    mock_validate_data.side_effect = ValueError("student_name is required")

    message_coordinator = MessageCoordinator.get_instance()
    message_data = {
        "tutor_phone": "+34612345678",
        "college_phone": "+34987654321",
        "message_content": "Hello, world!",
    }
    result = await message_coordinator.process_message(
        message_data, message_coordinator.send_response
    )
    assert result["status"] == "error"
    assert "student_name is required" in result["message"]
    mock_validate_data.assert_called_once_with(message_data)
