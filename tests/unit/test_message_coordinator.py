import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, patch
import pytest
from backend.services.message_coordinator import MessageCoordinator, MessageData

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
        "tutor_name": "Test Parent"
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
        "+14155552671"   # USA
    ]
    invalid_phones = [
        "",
        "abc123",
        "+",
        "12",
        "+34ABC123456",
        "666777888",     # Falta código país
        "+441234567890", # UK no soportado
        "+34555555555",  # España: no empieza por 6,7,8,9
        "+1123",         # USA: menos de 10 dígitos
        "+1123456789012" # USA: más de 10 dígitos
    ]

    for phone in valid_phones:
        assert coordinator._validate_phone_number(phone), f"Should be valid: {phone}"

    for phone in invalid_phones:
        assert not coordinator._validate_phone_number(phone), f"Should be invalid: {phone}"


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
    invalid_data = {
        "message_content": "Test message"
    }

    with pytest.raises(ValueError) as exc_info:
        coordinator._validate_message_data(invalid_data)
    assert "student_name is required" in str(exc_info.value)

@pytest.mark.asyncio
@pytest.mark.unittest
async def test_process_message_success(coordinator, valid_message_data):
    """Prueba el procesamiento exitoso de un mensaje."""
    mock_callback = AsyncMock()

    with patch('backend.services.attendance.AttendanceManager.process_whatsapp_message') as mock_process:
        mock_process.return_value = {
            "status": "success",
            "response": "Message processed successfully"
        }

        result = await coordinator.process_message(valid_message_data, mock_callback)

        assert result["status"] == "success"
        assert "timestamp" in result
        assert result["processing_completed"] is True
        mock_callback.assert_called_once_with(
            valid_message_data["tutor_phone"],
            "Message processed successfully"
        )

@pytest.mark.asyncio
@pytest.mark.unittest
async def test_process_message_validation_error(coordinator):
    """Prueba el manejo de errores de validación."""
    invalid_data = {
        "student_name": "",  # Nombre vacío
        "tutor_phone": "invalid_phone"
    }
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

    with patch('backend.services.attendance.AttendanceManager.process_whatsapp_message') as mock_process:
        mock_process.return_value = {
            "status": "success",
            "response": "Test response"
        }

        result = await coordinator.process_message(valid_message_data, mock_callback)

        assert result["status"] == "success"
        assert "warning" in result
        assert "response delivery failed" in result["warning"]

@pytest.mark.asyncio
@pytest.mark.unittest
async def test_process_message_attendance_error(coordinator, valid_message_data):
    """Prueba el manejo de errores del AttendanceManager."""
    mock_callback = AsyncMock()

    with patch('backend.services.attendance.AttendanceManager.process_whatsapp_message') as mock_process:
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

    with patch('backend.services.attendance.AttendanceManager.process_whatsapp_message') as mock_process:
        mock_process.return_value = {
            "status": "success",
            "response": "Test response"
        }

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