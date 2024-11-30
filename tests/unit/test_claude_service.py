import json
import logging
from unittest.mock import AsyncMock, patch

import pytest

from backend.core import get_settings
from backend.services.claude import ClaudeService
from backend.services.whatsapp import MessageProvider, WhatsAppService

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("faker.factory").setLevel(logging.WARNING)


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_error_handling():
    """Prueba el manejo de errores en los servicios."""
    claude_service = ClaudeService.get_instance()
    mock_session = AsyncMock()
    with patch.object(claude_service, "_session", new=mock_session):
        # Parchear el método post de la sesión mock
        mock_session.post.return_value.__aenter__.return_value.json.return_value = {
            "content": [
                {
                    "text": json.dumps(
                        {
                            "sensitivity": 5,
                            "response": "This is a test response.",
                            "likely_to_be_on_leave_tomorrow": False,
                            "reach_out_tomorrow": True,
                        }
                    )
                }
            ]
        }

    settings = get_settings()
    # Configuración del servicio de WhatsApp
    service = WhatsAppService(
        provider=MessageProvider.CALLMEBOT,
        meta_api_key=None,
        callback_token=settings.WHATSAPP_CALLBACK_TOKEN,
    )
    await service.init_service()
    phone = "NOT_A_VALID_PHONENUMBER"

    # Mock del cliente HTTP
    with patch(
        "aiohttp.ClientSession.get",
        side_effect=ValueError(f"Invalid phone number: {phone}"),
    ) as mock_get:
        with pytest.raises(ValueError):
            await service.send_message(phone, "Test message")
    await service.close_service()


@pytest.fixture
def mock_claude_response():
    """Fixture para crear respuestas mock de Claude."""

    def create_response(
        sensitivity, response="Test response", leave_tomorrow=False, reach_out=True
    ):
        return json.dumps(
            {
                "sensitivity": sensitivity,
                "response": response,
                "likely_to_be_on_leave_tomorrow": leave_tomorrow,
                "reach_out_tomorrow": reach_out,
            }
        )

    return create_response


class MockResponse:
    def __init__(self, data):
        self._data = data

    async def json(self):
        return self._data


class AsyncContextManagerMock:
    def __init__(self, return_value):
        self.return_value = return_value
        self.enter_called = False
        self.exit_called = False

    async def __aenter__(self):
        self.enter_called = True
        return self.return_value

    async def __aexit__(self, exc_type, exc, tb):
        self.exit_called = True


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_interaction_sensitivity_calculation_generate_response_when_college():
    with patch("aiohttp.ClientSession") as mock_session_class:
        claude_service = ClaudeService.get_instance()

        mock_response = AsyncMock()
        mock_session = mock_session_class.return_value
        mock_session.post.return_value.__aenter__.return_value.json.return_value = {
            "content": [
                {
                    "text": json.dumps(
                        {
                            "sensitivity": 7,
                            "response": "Test response",
                            "likely_to_be_on_leave_tomorrow": False,
                            "reach_out_tomorrow": True,
                        }
                    )
                }
            ]
        }

        response = await claude_service.generate_response_when_college(
            "student_name", "El estudiante está enfermo"
        )
        assert response["sensitivity"] == 7


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_interaction_sensitivity_error_handling_generate_response_when_college():
    claude_service = ClaudeService.get_instance()

    mock_session = AsyncMock()
    mock_session.post.side_effect = Exception("API Error")
    mock_session.close = AsyncMock()
    claude_service._session = mock_session

    response = await claude_service.generate_response_when_college(
        "student_name", "El estudiante está enfermo"
    )

    assert response["sensitivity"] == 5
    assert "Error" in response["response"]
    assert not response["likely_to_be_on_leave_tomorrow"]
    assert not response["reach_out_tomorrow"]


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_interaction_sensitivity_invalid_json_generate_response_when_college():
    claude_service = ClaudeService.get_instance()

    mock_context = AsyncMock()
    mock_context.json.return_value = {"content": [{"text": "Invalid JSON response"}]}

    mock_session = AsyncMock()
    mock_session.post.return_value = mock_context
    mock_session.close = AsyncMock()
    claude_service._session = mock_session

    response = await claude_service.generate_response_when_college(
        "student_name", "El estudiante está enfermo"
    )

    assert response["sensitivity"] == 5
    assert isinstance(response["response"], str)


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_interaction_sensitivity_calculation_generate_response_when_tutor():
    with patch("aiohttp.ClientSession") as mock_session_class:
        claude_service = ClaudeService.get_instance()

        mock_response = AsyncMock()
        mock_session = mock_session_class.return_value
        mock_session.post.return_value.__aenter__.return_value.json.return_value = {
            "content": [
                {
                    "text": json.dumps(
                        {
                            "sensitivity": 7,
                            "response": "Test response",
                            "likely_to_be_on_leave_tomorrow": False,
                            "reach_out_tomorrow": True,
                        }
                    )
                }
            ]
        }

        response = await claude_service.generate_response_when_tutor(
            "El estudiante está enfermo"
        )
        assert response["sensitivity"] == 7


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_interaction_sensitivity_error_handling_generate_response_when_tutor():
    claude_service = ClaudeService.get_instance()

    mock_session = AsyncMock()
    mock_session.post.side_effect = Exception("API Error")
    mock_session.close = AsyncMock()
    claude_service._session = mock_session

    response = await claude_service.generate_response_when_tutor(
        "El estudiante está enfermo"
    )

    assert response["sensitivity"] == 5
    assert "Error" in response["response"]
    assert not response["likely_to_be_on_leave_tomorrow"]
    assert not response["reach_out_tomorrow"]


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_interaction_sensitivity_invalid_json_generate_response_when_tutor():
    claude_service = ClaudeService.get_instance()

    mock_context = AsyncMock()
    mock_context.json.return_value = {"content": [{"text": "Invalid JSON response"}]}

    mock_session = AsyncMock()
    mock_session.post.return_value = mock_context
    mock_session.close = AsyncMock()
    claude_service._session = mock_session

    response = await claude_service.generate_response_when_tutor(
        "El estudiante está enfermo"
    )

    assert response["sensitivity"] == 5
    assert isinstance(response["response"], str)


@pytest.fixture(autouse=True)
async def cleanup_claude_service():
    yield
    service = ClaudeService.get_instance()
    service._session = AsyncMock()
    service._session.close = AsyncMock()
    await service.close_session()
