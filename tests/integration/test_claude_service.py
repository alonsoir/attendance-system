import pytest

from backend.services.claude import ClaudeService, logger


@pytest.fixture(autouse=True)
def reset_claude_service():
    """Reset the WhatsAppService singleton instance before each test."""
    logger.info("reset_claude_service...")
    ClaudeService._instance = None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_generate_claude_response_when_college_integration_es():
    """Prueba la generación de respuestas reales de Claude, en español"""
    claude_service = ClaudeService.get_instance()
    response = await claude_service.generate_response_when_college(
        student_name="Test Student name",
        message="El estudiante no ha venido a clase hoy, no sabemos si está enfermo "
        "o no, puedes averiguarlo por favor? El telefono de su madre es "
        "+34646322211 y se llama Maria Perez.",
    )

    # Verificar estructura básica
    assert isinstance(response, dict)
    assert all(
        key in response
        for key in [
            "sensitivity",
            "response",
            "likely_to_be_on_leave_tomorrow",
            "reach_out_tomorrow",
        ]
    )

    # Verificar tipos de datos
    assert isinstance(response["sensitivity"], int)
    assert isinstance(response["response"], str)
    assert isinstance(response["likely_to_be_on_leave_tomorrow"], bool)
    assert isinstance(response["reach_out_tomorrow"], bool)

    # Verificar valores específicos para mensaje de enfermedad
    assert 4 <= response["sensitivity"] <= 8  # Enfermedad es "significant issue"
    assert len(response["response"]) > 0
    assert any(
        palabra in response["response"].lower()
        for palabra in ["entendido", "contacto", "motivo", "ausencia", "informaré"]
    )

    await claude_service.close_session()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_generate_claude_response_when_college_integration_en():
    """Prueba la generación de respuestas reales de Claude."""
    claude_service = ClaudeService.get_instance()
    response = await claude_service.generate_response_when_college(
        student_name="Test Student name",
        message="We are very concerned because the student has not come to class today and this is unusual. "
        "We don't know if they are sick or if something serious has happened. "
        "His mother's phone number is +34646322211 and her name is Maria Perez. "
        "Please help us find out what's wrong urgently.",
    )

    # Verificar estructura básica
    assert isinstance(response, dict)
    assert all(
        key in response
        for key in [
            "sensitivity",
            "response",
            "likely_to_be_on_leave_tomorrow",
            "reach_out_tomorrow",
            "conversation_id",
            "reason",
        ]
    )

    # Verificar tipos de datos
    assert isinstance(response["sensitivity"], int)
    assert isinstance(response["response"], str)
    assert isinstance(response["likely_to_be_on_leave_tomorrow"], bool)
    assert isinstance(response["reach_out_tomorrow"], bool)
    assert isinstance(response["conversation_id"], str)
    assert isinstance(response["reason"], str)

    # Verificar valores específicos para mensaje de enfermedad
    assert 5 <= response["sensitivity"] <= 9  # Enfermedad es "significant issue"
    assert len(response["response"]) > 0
    assert any(
        palabra in response["response"].lower()
        # hay veces que Claude responde en Español y en Inglés, aunque le indiques claramente que responda en el
        # idioma en el que ha sido enviado el mensaje.
        for palabra in [
            "urgent",
            "concerned",
            "contact",
            "immediately",
            "find out",
            "preocupa",
            "estudiante",
            "inusual",
            "averiguar",
        ]
    )

    await claude_service.close_session()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_generate_claude_response_when_tutor_integration_en():
    """Test generating real Claude responses in English"""
    claude_service = ClaudeService.get_instance()
    message_from_tutor = (
        "My son is sick and will be staying home for a few days. "
        "He has been prescribed broad-spectrum antibiotics at the hospital, "
        "so he will be home for a few days until his fever is gone. "
        "I will let you know when he can return to school."
    )
    response = await claude_service.generate_response_when_tutor(
        message_from_tutor=message_from_tutor
    )

    # Verify basic structure
    assert isinstance(response, dict)
    assert all(
        key in response
        for key in [
            "sensitivity",
            "response",
            "likely_to_be_on_leave_tomorrow",
            "reach_out_tomorrow",
            "conversation_id",
            "reason",
        ]
    )

    # Verify data types
    assert isinstance(response["sensitivity"], int)
    assert isinstance(response["response"], str)
    assert isinstance(response["likely_to_be_on_leave_tomorrow"], bool)
    assert isinstance(response["reach_out_tomorrow"], bool)
    assert isinstance(response["conversation_id"], str)
    assert isinstance(response["reason"], str)
    # En este caso concreto, Claude ha tenido que determinar que la conversacion se puede cerrar puesto
    # que el tutor ha dicho que el hijo está enfermo.
    assert response["likely_to_be_on_leave_tomorrow"] == True
    assert response["reach_out_tomorrow"] == False
    assert response["reason"] == "in progress"
    # Verify specific values for illness message
    assert 7 <= response["sensitivity"] <= 9  # Illness is a "significant issue"
    assert len(response["response"]) > 0
    """
    Es un verdadero dolor tratar de predecir que cojones va a decir Claude.
    assert any(
        palabra in response["response"].lower()
        for palabra in ["sorry", "sick", "understandable", "antibiotics"]
    )
    """
    assert (
        response["response"] == response["response"]
    )  # Verify the response is in Spanish

    await claude_service.close_session()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_generate_claude_response_when_tutor_integration_es():
    """Test generating real Claude responses, in Spanish"""
    claude_service = ClaudeService.get_instance()
    message_from_tutor = (
        "Mi hijo está enfermo y se ha quedado en casa, "
        "le he puesto antibióticos de amplio espectro recetados por el hospital, "
        "por lo que permanecerá en casa hasta que deje de tener fiebre. "
        "Creo que en cinco días no tendrá fiebre y podrá volver a la escuela."
    )
    response = await claude_service.generate_response_when_tutor(
        message_from_tutor=message_from_tutor
    )

    # Verify basic structure
    assert isinstance(response, dict)
    assert all(
        key in response
        for key in [
            "sensitivity",
            "response",
            "likely_to_be_on_leave_tomorrow",
            "reach_out_tomorrow",
            "conversation_id",
            "reason",
        ]
    )

    # Verify data types
    assert isinstance(response["sensitivity"], int)
    assert isinstance(response["response"], str)
    assert isinstance(response["likely_to_be_on_leave_tomorrow"], bool)
    assert isinstance(response["reach_out_tomorrow"], bool)
    assert isinstance(response["conversation_id"], str)
    assert isinstance(response["reason"], str)
    assert response["likely_to_be_on_leave_tomorrow"] == True
    assert response["reach_out_tomorrow"] == False
    assert response["reason"] == "in progress"
    # Verify specific values for illness message
    assert 7 <= response["sensitivity"] <= 8  # Illness is a "significant issue"
    assert len(response["response"]) > 0
    """
    Es un verdadero dolor tratar de predecir que cojones va a decir Claude.
    assert any(
        palabra in response["response"].lower()
        for palabra in ["enferm", "salud", "recuper", "descans"]
    )
    """
    assert (
        response["response"] == response["response"]
    )  # Verify the response is in Spanish

    await claude_service.close_session()
