import pytest


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_phone_number_validation():
    """Prueba la validación de números de teléfono."""
    from backend.services import PhoneNumberValidator

    # Números españoles válidos
    assert PhoneNumberValidator.validate_phone("+34666777888")
    assert PhoneNumberValidator.validate_phone("+34911234567")

    # Números estadounidenses válidos
    assert PhoneNumberValidator.validate_phone("+12125551234")
    assert PhoneNumberValidator.validate_phone("+19175551234")

    # Números inválidos
    assert not PhoneNumberValidator.validate_phone("+1212555")
    assert not PhoneNumberValidator.validate_phone("+3466677")
    assert not PhoneNumberValidator.validate_phone("invalid")


@pytest.mark.asyncio
@pytest.mark.unittest
async def test_message_formatter():
    """Prueba el formateador de mensajes."""
    from backend.services import MessageFormatter

    # Prueba con diferentes idiomas
    es_message = MessageFormatter.get_message(
        "INITIAL_CONTACT", "es-ES", student_name="Juan", school_name="IES Test"
    )
    assert "Juan" in es_message
    assert "IES Test" in es_message

    en_message = MessageFormatter.get_message(
        "INITIAL_CONTACT", "en-US", student_name="John", school_name="Test High School"
    )
    assert "John" in en_message
    assert "Test High School" in en_message
