import pytest
from backend.services.whatsapp import WhatsAppService, MessageProvider, settings


@pytest.mark.asyncio
@pytest.mark.integration
async def test_send_message_to_callmebot_integration():
    # Configuración del servicio
    service = WhatsAppService(meta_api_key=settings.WHATSAPP_CALLBACK_TOKEN, provider=MessageProvider.CALLMEBOT)
    phone = "+34667519829"  # Cambia esto por tu número de pruebas
    message = "Hello, this is a real integration test."

    # Llamada al servicio real
    response = await service._send_callmebot_message(phone=phone, message=message)

    # Verificaciones
    assert response["status"] == "success"
    assert response["provider"] == "callmebot"
    assert "Message queued" in response["response"]
    assert "You will receive it in a few seconds." in response["response"]

import pytest
from backend.services.claude import generate_claude_response

@pytest.mark.integration
@pytest.mark.asyncio
async def test_generate_claude_response_integration():
    """Prueba la generación de respuestas reales de Claude."""
    response = await generate_claude_response("Test Student")

    assert "content" in response
    assert any(
        "absence" in msg["text"] or "support" in msg["text"]
        for msg in response["content"]
    )
