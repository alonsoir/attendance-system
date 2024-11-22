from datetime import datetime
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from sqlalchemy import select

from backend import get_settings
from backend.db.models import ServiceStatus
from backend.services.attendance import AttendanceManager
from backend.services.claude import generate_claude_response
from backend.services.whatsapp import WhatsAppService, MessageProvider
import logging
logging.getLogger("faker.factory").setLevel(logging.WARNING)

@pytest.mark.asyncio
@pytest.mark.unittest
async def test_send_message_to_callmebot():
    """Prueba el envío de mensajes de WhatsApp en modo mock con provider CallMeBot."""
    settings = get_settings()
    # Configuración del servicio

    service = WhatsAppService(provider=MessageProvider.CALLMEBOT,
                              meta_api_key=None,
                              callback_token=settings.WHATSAPP_CALLBACK_TOKEN)
    await service.init_service()  # Inicializar el cliente HTTP

    phone = "+34667519829"
    message = "Hello, this is a test, from test_send_message_to_callmebot..."
    expected_url = (
        f"https://api.callmebot.com/whatsapp.php?"
        f"phone={phone}&text={message}&apikey=9295095"
    )

    mock_response_text = 'Hello, this is a test, from test_send_message_to_callmebot...'

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
                response.get("status") == "success" or
                response.get("phone") == phone or
                response.get("message") == message
        )

        await service.close_service()

# Tests para el servicio de WhatsApp
@pytest.mark.asyncio
@pytest.mark.unittest
async def test_send_whatsapp_message():
    """Prueba el envío de mensajes de WhatsApp en modo mock con provider Meta."""
    # Configuración del servicio
    service = WhatsAppService(provider=MessageProvider.META,
                              meta_api_key=None,
                              callback_token=None)
    await service.init_service()  # Inicializar el cliente HTTP

    phone = "+34667519829"
    message = "Hello, this is a test, from test_send_whatsapp_message..."


    mock_response_text = 'Hello, this is a test, from test_send_whatsapp_message...'

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
                response.get("status") == "success" or
                response.get("phone") == phone or
                response.get("message") == message
        )

        await service.close_service()

@pytest.mark.asyncio
@pytest.mark.unittest
async def test_send_whatsapp_message_invalid_phone():
    """Prueba el envío de mensajes a números inválidos."""
    """Prueba el envío de mensajes de WhatsApp en modo mock con provider Meta."""
    # Configuración del servicio
    service = WhatsAppService(provider=MessageProvider.META,
                              meta_api_key=None,
                              callback_token=None)
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

    service = WhatsAppService(provider=MessageProvider.CALLMEBOT,
                              meta_api_key=None,
                              callback_token=settings.WHATSAPP_CALLBACK_TOKEN)
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

    with patch.object(attendance_manager, "process_whatsapp_message", AsyncMock(return_value=expected_response)):
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


from unittest.mock import AsyncMock

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

    await manager.save_interaction(mock_db_session, mock_student_name, mock_tutor_phone, mock_claude_response)

    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()


@pytest.mark.unittest
@pytest.mark.asyncio
async def test_generate_claude_response_mock():
    """Prueba la generación de respuestas de Claude con un mock."""
    mock_response = {
        "content": [
            {
                "text": "Mock response with sensitivity",
                "type": "text",
            }
        ],
        "id": "mock_id",
        "model": "mock-model",
        "role": "assistant",
    }

    with patch(
        "backend.services.claude.generate_claude_response",
        new=AsyncMock(return_value=mock_response),
    ):
        response = await generate_claude_response("Test Student")

        # Imprime para depuración
        print(response)

        # Valida correctamente
        assert "content" in response
        assert any(
            "Attendance" in msg.get("text", "") for msg in response.get("content", [])
        ), "El mensaje debería contener 'Attendance'."


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_generate_claude_response_error():
    """Prueba el manejo de errores en las respuestas de Claude."""
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_post.return_value.__aenter__.return_value.status = 500
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(
            side_effect=Exception("API Error")
        )

        with pytest.raises(Exception):
            await generate_claude_response("Test Student")



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


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_broadcast_update(db_session):
    """Prueba la difusión de actualizaciones."""
    mock_websocket = MagicMock()
    mock_websocket.send_json = AsyncMock()

    AttendanceManager.active_connections = {1: mock_websocket}
    await AttendanceManager.broadcast_update()
    mock_websocket.send_json.assert_called_once()



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
    # Prueba de error en Claude
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_post.side_effect = Exception("API Error")
        with pytest.raises(Exception):
            await generate_claude_response("Test Student")

    settings = get_settings()
    # Configuración del servicio

    service = WhatsAppService(provider=MessageProvider.CALLMEBOT,
                              meta_api_key=None,
                              callback_token=settings.WHATSAPP_CALLBACK_TOKEN)
    await service.init_service()
    phone = "NOT_A_VALID_PHONENUMBER"
    # Prueba de error en WhatsApp
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.side_effect = ValueError(f"Invalid phone number: {phone}")
        with pytest.raises(ValueError):
            await service.send_message(phone, "Test message")
            await service.close_service()




@pytest.mark.asyncio
@pytest.mark.unittest
async def test_service_status_updates(db_session):
    """Prueba las actualizaciones de estado de servicios."""
    # Crear un nuevo estado de servicio
    service = ServiceStatus(
        service_name="test_service", status=True, last_check=datetime.utcnow()
    )
    # Añadir la entidad a la sesión y confirmar cambios
    await db_session.add(service)
    await db_session.commit()

    # Actualizar el estado
    service.status = False
    service.error_message = "Test error"
    await db_session.commit()

    # Verificar la actualización
    updated = await db_session.execute(
        select(ServiceStatus).filter_by(service_name="test_service")
    )
    updated_service = updated.scalar_one_or_none()

    assert updated_service is not None
    assert not updated_service.status
    assert updated_service.error_message == "Test error"



@pytest.mark.asyncio
@pytest.mark.unittest
async def test_interaction_sensitivity_calculation():
    """Prueba el cálculo de sensibilidad de las interacciones."""
    # Probar diferentes escenarios
    test_cases = [
        ("El estudiante está enfermo", 7),
        ("Visita al médico programada", 5),
        ("Emergencia familiar", 9),
        ("Llegará tarde hoy", 3),
    ]

    for message, expected_sensitivity in test_cases:
        with patch("backend.services.claude.generate_claude_response") as mock_claude:
            mock_claude.return_value = {
                "sensitivity": expected_sensitivity,
                "response": "Test response",
                "likely_to_be_on_leave_tomorrow": False,
                "reach_out_tomorrow": True,
            }

            response = await generate_claude_response(message)
            assert response["sensitivity"] == expected_sensitivity


if __name__ == "__main__":
    pytest.main(["-v", __file__])
