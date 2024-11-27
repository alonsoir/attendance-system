from unittest.mock import patch, AsyncMock

import pytest

from backend import get_settings
from backend.services.whatsapp import WhatsAppService, MessageProvider


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