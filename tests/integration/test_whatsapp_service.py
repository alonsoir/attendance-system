import pytest
from aiohttp import ClientResponseError


@pytest.fixture(autouse=True)
def reset_whatsapp_service():
    """Reset the WhatsAppService singleton instance before each test."""
    WhatsAppService._instance = None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_send_message_to_callmebot_integration():
    # Configuración del servicio
    settings = get_settings()
    # Configuración del servicio

    service = WhatsAppService(
        provider=MessageProvider.CALLMEBOT,
        meta_api_key=settings.WHATSAPP_CALLBACK_TOKEN,
        callback_token=settings.WHATSAPP_CALLBACK_TOKEN,
    )
    await service.initialize()  # Inicializar el cliente HTTP

    phone = "+34667519829"  # Cambia esto por tu número de pruebas
    message = "Hello, this is a real integration test from test_send_message_to_callmebot_integration."

    # Llamada al servicio real
    response = await service.send_message(phone=phone, message=message)

    # Verificaciones
    assert response["status"] == "success"
    assert response["provider"] == "callmebot"
    assert "Message queued" in response["response"]
    assert "You will receive it in a few seconds." in response["response"]
    await service.close()


import pytest
from aioresponses import aioresponses

from backend.core.config import get_settings
from backend.services.whatsapp import MessageProvider, WhatsAppService


@pytest.mark.asyncio
@pytest.mark.integration
async def test_send_whatsapp_message():
    settings = get_settings()

    """Prueba el envío de mensajes de WhatsApp con provider Meta."""
    service = WhatsAppService(
        provider=MessageProvider.META,
        meta_api_key=settings.WHATSAPP_META_API_KEY,  # Use the actual API key from settings
        callback_token=settings.WHATSAPP_CALLBACK_TOKEN,
    )
    await service.initialize()

    phone = "+34667519829"
    message = "Hello, this is a test..."

    with aioresponses() as m:
        m.post(
            f"https://graph.facebook.com/v16.0/me/messages?access_token={settings.WHATSAPP_META_API_KEY}",
            status=400,
            body="Bad Request",
            repeat=True,
        )

        with pytest.raises(ClientResponseError, match="400, message='Bad Request'"):
            await service.send_message(phone=phone, message=message)

    await service.close()
