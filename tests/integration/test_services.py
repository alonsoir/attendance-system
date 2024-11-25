import pytest

from backend import get_settings
from backend.services import generate_claude_response
from backend.services.claude import ClaudeService
from backend.services.whatsapp import WhatsAppService, MessageProvider, settings


@pytest.mark.asyncio
@pytest.mark.integration
async def test_send_message_to_callmebot_integration():
    # Configuración del servicio
    settings = get_settings()
    # Configuración del servicio

    service = WhatsAppService(provider=MessageProvider.CALLMEBOT,
                              meta_api_key=settings.WHATSAPP_CALLBACK_TOKEN,
                              callback_token=settings.WHATSAPP_CALLBACK_TOKEN)
    await service.init_service()  # Inicializar el cliente HTTP

    phone = "+34667519829"  # Cambia esto por tu número de pruebas
    message = "Hello, this is a real integration test from test_send_message_to_callmebot_integration."

    # Llamada al servicio real
    response = await service.send_message(phone=phone, message=message)

    # Verificaciones
    assert response["status"] == "success"
    assert response["provider"] == "callmebot"
    assert "Message queued" in response["response"]
    assert "You will receive it in a few seconds." in response["response"]



@pytest.mark.integration
@pytest.mark.asyncio
async def test_generate_claude_response_integration():
    """Prueba la generación de respuestas reales de Claude."""
    claude_service = ClaudeService.get_instance()
    response = await claude_service.generate_response(student_name="Test Student",message="El estudiante está enfermo.")

    assert "content" in response
    assert any(
        "absence" in msg["text"] or "support" in msg["text"]
        for msg in response["content"]
    )
