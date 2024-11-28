import pytest
from backend.services.claude import ClaudeService


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
    assert 5 <= response["sensitivity"] <= 8  # Enfermedad es "significant issue"
    assert len(response["response"]) > 0
    assert any(
        palabra in response["response"].lower()
        for palabra in ["entendido", "contacto", "motivo", "ausencia", "informaré"]
    )

    await claude_service.close_session()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_generate_claude_response_when_college_integration_en():
    """Prueba la generación de respuestas reales de Claude, en español"""
    claude_service = ClaudeService.get_instance()
    response = await claude_service.generate_response_when_college(
        student_name="Test Student name",
        message="The student has not come to class today, we don't know if he is sick or not, can you please find out? "
        "His mother's phone number is +34646322211 and her name is Maria Perez.",
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
    assert 5 <= response["sensitivity"] <= 8  # Enfermedad es "significant issue"
    assert len(response["response"]) > 0
    assert any(
        palabra in response["response"].lower()
        for palabra in ["entendido", "contacto", "motivo", "ausencia", "informaré"]
    )

    await claude_service.close_session()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_generate_claude_response_when_tutor_integration_en():
    """Test generating real Claude responses, in Spanish"""
    claude_service = ClaudeService.get_instance()
    message_from_tutor = "My son is sick and has stayed home, I have put him on broad spectrum antibiotics prescribed by the hospital."
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
        ]
    )

    # Verify data types
    assert isinstance(response["sensitivity"], int)
    assert isinstance(response["response"], str)
    assert isinstance(response["likely_to_be_on_leave_tomorrow"], bool)
    assert isinstance(response["reach_out_tomorrow"], bool)

    # Verify specific values for illness message
    assert 7 <= response["sensitivity"] <= 8  # Illness is a "significant issue"
    assert len(response["response"]) > 0
    assert any(
        palabra in response["response"].lower()
        for palabra in ["sorry", "sick", "understandable", "antibiotics"]
    )
    assert (
        response["response"] == response["response"]
    )  # Verify the response is in Spanish

    await claude_service.close_session()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_generate_claude_response_when_tutor_integration_es():
    """Test generating real Claude responses, in Spanish"""
    claude_service = ClaudeService.get_instance()
    message_from_tutor = "Mi hijo está enfermo y se ha quedado en casa, le he puesto antibióticos de amplio espectro recetados por el hospital."
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
        ]
    )

    # Verify data types
    assert isinstance(response["sensitivity"], int)
    assert isinstance(response["response"], str)
    assert isinstance(response["likely_to_be_on_leave_tomorrow"], bool)
    assert isinstance(response["reach_out_tomorrow"], bool)

    # Verify specific values for illness message
    assert 7 <= response["sensitivity"] <= 8  # Illness is a "significant issue"
    assert len(response["response"]) > 0
    assert any(
        palabra in response["response"].lower()
        for palabra in ["enferm", "salud", "recuper", "descans"]
    )
    assert (
        response["response"] == response["response"]
    )  # Verify the response is in Spanish

    await claude_service.close_session()
