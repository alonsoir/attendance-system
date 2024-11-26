import pytest

from backend import get_settings
from backend.services.claude import ClaudeService
from backend.services.whatsapp import WhatsAppService, MessageProvider


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
async def test_generate_claude_response_integration_es():
    """Prueba la generación de respuestas reales de Claude, en español"""
    claude_service = ClaudeService.get_instance()
    response = await claude_service.generate_response(student_name="Test Student",message="El estudiante está enfermo.")

    # Verificar estructura básica
    assert isinstance(response, dict)
    assert all(
        key in response for key in ["sensitivity", "response", "likely_to_be_on_leave_tomorrow", "reach_out_tomorrow"])

    # Verificar tipos de datos
    assert isinstance(response["sensitivity"], int)
    assert isinstance(response["response"], str)
    assert isinstance(response["likely_to_be_on_leave_tomorrow"], bool)
    assert isinstance(response["reach_out_tomorrow"], bool)

    # Verificar valores específicos para mensaje de enfermedad
    assert 7 <= response["sensitivity"] <= 8  # Enfermedad es "significant issue"
    assert len(response["response"]) > 0
    assert any(palabra in response["response"].lower() for palabra in ["enferm", "salud", "recuper", "descans"])

    await claude_service.close_session()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_generate_claude_response_integration_english():
    """Prueba la generación de respuestas reales de Claude, en ingles"""
    claude_service = ClaudeService.get_instance()
    response = await claude_service.generate_response(student_name="Test Student",message="The student is sick.")

    # Verificar estructura básica
    assert isinstance(response, dict)
    assert all(
        key in response for key in ["sensitivity", "response", "likely_to_be_on_leave_tomorrow", "reach_out_tomorrow"])

    # Verificar tipos de datos
    assert isinstance(response["sensitivity"], int)
    assert isinstance(response["response"], str)
    assert isinstance(response["likely_to_be_on_leave_tomorrow"], bool)
    assert isinstance(response["reach_out_tomorrow"], bool)

    # Verificar valores específicos para mensaje de enfermedad
    assert 7 <= response["sensitivity"] <= 8  # Enfermedad es "significant issue"
    assert len(response["response"]) > 0
    assert any(palabra in response["response"].lower() for palabra in ["sorry", "health", "well-being", "focus","resting",
                                                                       "excuse","absence"])
    # "i'm sorry to hear you are not feeling well. your health and well-being are most important. please focus on resting and recovering. i will excuse your absence and notify your teachers. feel better soon."
    await claude_service.close_session()

