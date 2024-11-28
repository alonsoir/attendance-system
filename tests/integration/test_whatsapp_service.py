import pytest
from aiohttp import ClientResponseError

from backend import get_settings
from backend.services.whatsapp import WhatsAppService, MessageProvider


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


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_send_whatsapp_message():
    """Prueba el envío de mensajes de WhatsApp con provider Meta. Verifica NotImplementedError."""
    service = WhatsAppService(
        provider=MessageProvider.META,
        meta_api_key="",  # Dejamos el meta_api_key vacío para provocar la excepción
        callback_token="",  # Dejamos el callback_token vacío para provocar la excepción
    )
    await service.init_service()

    phone = "+34667519829"
    message = "Hello, this is a test..."

    with pytest.raises(ClientResponseError, match="400, message='Bad Request'"):
        await service.send_message(phone=phone, message=message)

    await service.close_service()
