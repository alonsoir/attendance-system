from unittest.mock import patch

import pytest
from aiohttp import ClientResponseError

from backend.api.endpoints.whatsapp import settings
from backend.core import get_settings
from backend.services.whatsapp import MessageProvider, WhatsAppService


@pytest.fixture(autouse=True)
def reset_whatsapp_service():
    """Reset the WhatsAppService singleton instance before each test."""
    WhatsAppService._instance = None


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_send_message_to_callmebot():
    """Prueba el envío de mensajes de WhatsApp en modo mock con provider CallMeBot."""
    settings = get_settings()
    service = WhatsAppService(
        provider=MessageProvider.CALLMEBOT,
        meta_api_key=None,
        callback_token=settings.WHATSAPP_CALLBACK_TOKEN,
    )

    try:
        await service.initialize()
        phone = "+34667519829"
        message = "Hello, this is a test, from test_send_message_to_callmebot..."

        mock_response = AsyncMock()
        mock_response.text = AsyncMock(return_value=message)
        mock_response.status = 200
        mock_response.raise_for_status = AsyncMock()

        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response
            response = await service.send_message(phone=phone, message=message)

            assert response.get("status") == "success"
            assert response.get("phone") == phone
            assert response.get("message") == message
            mock_response.raise_for_status.assert_called_once()

    finally:
        await service.close()


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_send_whatsapp_message():
    """Prueba el envío de mensajes de WhatsApp con provider Meta. Verifica NotImplementedError."""
    service = WhatsAppService(
        provider=MessageProvider.META,
        meta_api_key="",  # Dejamos el meta_api_key vacío para provocar la excepción
        callback_token="",  # Dejamos el callback_token vacío para provocar la excepción
    )
    await service.initialize()
    phone = "+34667519829"
    message = "Hello, this is a test..."

    with pytest.raises(ClientResponseError, match="400, message='Bad Request'"):
        await service._send_meta_message(phone=phone, message=message)

    await service.close()


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_send_whatsapp_message_invalid_phone():
    """Prueba el envío de mensajes a números inválidos."""
    """Prueba el envío de mensajes de WhatsApp en modo mock con provider Meta."""
    # Configuración del servicio
    service = WhatsAppService(
        provider=MessageProvider.META, meta_api_key=None, callback_token=None
    )
    await service.initialize()
    with pytest.raises(ValueError):
        await service.send_message("invalid-phone", "Test message")
        await service.close()


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
    await service.initialize()
    with pytest.raises(ValueError):
        await service.send_message("invalid-phone", "Test message")
        await service.close()


from unittest.mock import AsyncMock

import aiohttp


async def test_send_message_meta_provider():
    service = WhatsAppService()
    service._http_client = AsyncMock(aiohttp.ClientSession)
    service._http_client.post.return_value.__aenter__.return_value.json.return_value = {
        "success": True
    }
    response = await service.send_message("+34667519829", "Hello, this is a test...")
    assert response["status"] == "success"


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_verify_callback():
    service = WhatsAppService(
        provider=MessageProvider.META,
        meta_api_key=settings.WHATSAPP_META_API_KEY,
        callback_token=settings.WHATSAPP_CALLBACK_TOKEN,
    )
    await service.initialize()
    assert await service.verify_callback(settings.WHATSAPP_CALLBACK_TOKEN)
    assert not await service.verify_callback("invalid_token")
    await service.close()
