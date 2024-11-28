from unittest.mock import patch, AsyncMock

import pytest
from aiohttp import ClientResponseError

from backend import get_settings
from backend.services.whatsapp import WhatsAppService, MessageProvider


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_send_message_to_callmebot():
    """Prueba el envío de mensajes de WhatsApp en modo mock con provider CallMeBot."""
    settings = get_settings()
    # Configuración del servicio

    service = WhatsAppService(
        provider=MessageProvider.CALLMEBOT,
        meta_api_key=None,
        callback_token=settings.WHATSAPP_CALLBACK_TOKEN,
    )
    await service.init_service()  # Inicializar el cliente HTTP

    phone = "+34667519829"
    message = "Hello, this is a test, from test_send_message_to_callmebot..."
    expected_url = (
        f"https://api.callmebot.com/whatsapp.php?"
        f"phone={phone}&text={message}&apikey=9295095"
    )

    mock_response_text = "Hello, this is a test, from test_send_message_to_callmebot..."

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
            response.get("status") == "success"
            or response.get("phone") == phone
            or response.get("message") == message
        )

        await service.close_service()


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
        await service._send_meta_message(phone=phone, message=message)

    await service.close_service()


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_send_whatsapp_message_invalid_phone():
    """Prueba el envío de mensajes a números inválidos."""
    """Prueba el envío de mensajes de WhatsApp en modo mock con provider Meta."""
    # Configuración del servicio
    service = WhatsAppService(
        provider=MessageProvider.META, meta_api_key=None, callback_token=None
    )
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

    service = WhatsAppService(
        provider=MessageProvider.CALLMEBOT,
        meta_api_key=None,
        callback_token=settings.WHATSAPP_CALLBACK_TOKEN,
    )
    await service.init_service()

    with pytest.raises(ValueError):
        await service.send_message("invalid-phone", "Test message")
        await service.close_service()


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_send_message_meta_provider():
    service = WhatsAppService(
        provider=MessageProvider.META,
        meta_api_key="test_api_key",
        callback_token=get_settings().WHATSAPP_CALLBACK_TOKEN,
    )
    await service.init_service()

    phone = "+34667519829"
    message = "Hello, this is a test..."

    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value={"message_id": "123456789"})
    mock_response.status = 200

    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_post.return_value.__aenter__.return_value = mock_response
        response = await service.send_message(phone, message)
        assert response["status"] == "success"
        assert response["provider"] == "meta"

    await service.close_service()


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_verify_callback():
    service = WhatsAppService(
        provider=MessageProvider.META,
        meta_api_key="test_api_key",
        callback_token="test_token",
    )
    assert await service.verify_callback("test_token")
    assert not await service.verify_callback("invalid_token")


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_get_status():
    service = WhatsAppService(
        provider=MessageProvider.META,
        meta_api_key="test_api_key",
        callback_token="test_token",
    )
    status = service.get_status()
    assert status["mode"] == "live"
    assert status["provider"] == "meta"
    assert status["features_enabled"]["sending"]
    assert status["features_enabled"]["callbacks"]

    service = WhatsAppService(
        provider=MessageProvider.MOCK,
        meta_api_key=None,
        callback_token=None,
    )
    status = service.get_status()
    assert status["mode"] == "mock"
    assert status["provider"] == "mock"
    assert not status["features_enabled"]["sending"]
    assert status["features_enabled"]["callbacks"]
