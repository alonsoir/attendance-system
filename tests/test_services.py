from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.db.models import Interaction, ServiceStatus
from backend.services.attendance import AttendanceManager
from backend.services.claude import generate_claude_response
from backend.services.whatsapp import handle_whatsapp_message, send_whatsapp_message


# Tests para el servicio de Claude
@pytest.mark.asyncio
async def test_generate_claude_response():
    '''Prueba la generación de respuestas de Claude.'''
    # Configurar mock para la llamada a la API
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(
            return_value={
                'sensitivity': 5,
                'response': 'Test response',
                'likely_to_be_on_leave_tomorrow': False,
                'reach_out_tomorrow': True,
            }
        )
        mock_post.return_value.__aenter__.return_value.status = 200

        response = await generate_claude_response('Test Student')
        assert 'sensitivity' in response
        assert 'response' in response


@pytest.mark.asyncio
async def test_generate_claude_response_error():
    '''Prueba el manejo de errores en las respuestas de Claude.'''
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_post.return_value.__aenter__.return_value.status = 500
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(
            side_effect=Exception('API Error')
        )

        with pytest.raises(Exception):
            await generate_claude_response('Test Student')


# Tests para el servicio de WhatsApp
@pytest.mark.asyncio
async def test_send_whatsapp_message():
    '''Prueba el envío de mensajes de WhatsApp en modo mock.'''
    from backend.services.whatsapp import whatsapp_service

    response = await send_whatsapp_message('+34666777888', 'Test message')

    # Verificar la respuesta del mock
    assert response['status'] == 'success'
    assert response['mock'] is True
    assert response['phone'] == '+34666777888'
    assert response['message'] == 'Test message'
    assert 'timestamp' in response


@pytest.mark.asyncio
async def test_send_whatsapp_message_invalid_phone():
    '''Prueba el envío de mensajes a números inválidos.'''
    with pytest.raises(ValueError):
        await send_whatsapp_message('invalid-phone', 'Test message')


@pytest.mark.asyncio
async def test_handle_whatsapp_message(mock_whatsapp_message):
    '''Prueba el manejo de mensajes de WhatsApp.'''
    with patch(
        'backend.services.attendance.AttendanceManager.process_whatsapp_message'
    ) as mock_process:
        mock_process.return_value = {
            'status': 'success',
            'response': {
                'sensitivity': 5,
                'response': 'Test response',
                'likely_to_be_on_leave_tomorrow': False,
                'reach_out_tomorrow': True,
            },
        }

        result = await handle_whatsapp_message(mock_whatsapp_message)
        assert result['status'] == 'success'
        assert 'response' in result


# Tests para el AttendanceManager
@pytest.mark.asyncio
async def test_attendance_manager_process_message(
    db_session, test_user, mock_whatsapp_message
):
    '''Prueba el procesamiento de mensajes por el AttendanceManager.'''
    with patch('backend.services.claude.generate_claude_response') as mock_claude:
        mock_claude.return_value = {
            'sensitivity': 5,
            'response': 'Test response',
            'likely_to_be_on_leave_tomorrow': False,
            'reach_out_tomorrow': True,
        }

        result = await AttendanceManager.process_whatsapp_message(mock_whatsapp_message)
        assert result['status'] == 'success'
        assert 'response' in result


@pytest.mark.asyncio
async def test_check_service_status():
    '''Prueba la verificación del estado de los servicios.'''
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 200

        status = await AttendanceManager.check_service_status()
        assert isinstance(status, dict)
        assert 'claude' in status
        assert 'meta' in status
        assert all(isinstance(v, bool) for v in status.values())


@pytest.mark.asyncio
async def test_broadcast_update(db_session):
    '''Prueba la difusión de actualizaciones.'''
    mock_websocket = MagicMock()
    mock_websocket.send_json = AsyncMock()

    AttendanceManager.active_connections = {1: mock_websocket}
    await AttendanceManager.broadcast_update()
    mock_websocket.send_json.assert_called_once()


@pytest.mark.asyncio
async def test_save_interaction(db_session, test_user):
    '''Prueba el guardado de interacciones.'''
    interaction_data = {
        'student_name': 'Test Student',
        'tutor_phone': '+34666777888',
        'claude_response': {
            'sensitivity': 5,
            'response': 'Test response',
            'likely_to_be_on_leave_tomorrow': False,
            'reach_out_tomorrow': True,
        },
    }

    await AttendanceManager.save_interaction(
        interaction_data['student_name'],
        interaction_data['tutor_phone'],
        interaction_data['claude_response'],
    )

    saved = (
        db_session.query(Interaction)
        .filter_by(student_name=interaction_data['student_name'])
        .first()
    )
    assert saved is not None
    assert saved.tutor_phone == interaction_data['tutor_phone']


@pytest.mark.asyncio
async def test_verify_authorization():
    '''Prueba la verificación de autorización.'''
    result = await AttendanceManager.verify_authorization(
        'Test Student', '+34666777888'
    )
    assert isinstance(result, bool)


@pytest.mark.asyncio
async def test_get_dashboard_data(db_session, test_interaction):
    '''Prueba la obtención de datos para el dashboard.'''
    data = await AttendanceManager.get_dashboard_data()
    assert 'service_status' in data
    assert 'interactions' in data
    assert isinstance(data['interactions'], list)
    assert len(data['interactions']) > 0


@pytest.mark.asyncio
async def test_phone_number_validation():
    '''Prueba la validación de números de teléfono.'''
    from backend.services import PhoneNumberValidator

    # Números españoles válidos
    assert PhoneNumberValidator.validate_phone('+34666777888', 'ES')
    assert PhoneNumberValidator.validate_phone('+34911234567', 'ES')

    # Números estadounidenses válidos
    assert PhoneNumberValidator.validate_phone('+12125551234', 'US')
    assert PhoneNumberValidator.validate_phone('+19175551234', 'US')

    # Números inválidos
    assert not PhoneNumberValidator.validate_phone('+1212555', 'US')
    assert not PhoneNumberValidator.validate_phone('+3466677', 'ES')
    assert not PhoneNumberValidator.validate_phone('invalid', 'ES')


@pytest.mark.asyncio
async def test_message_formatter():
    '''Prueba el formateador de mensajes.'''
    from backend.services import MessageFormatter

    # Prueba con diferentes idiomas
    es_message = MessageFormatter.get_message(
        'INITIAL_CONTACT', 'es-ES', student_name='Juan', school_name='IES Test'
    )
    assert 'Juan' in es_message
    assert 'IES Test' in es_message

    en_message = MessageFormatter.get_message(
        'INITIAL_CONTACT', 'en-US', student_name='John', school_name='Test High School'
    )
    assert 'John' in en_message
    assert 'Test High School' in en_message


@pytest.mark.asyncio
async def test_error_handling():
    '''Prueba el manejo de errores en los servicios.'''
    # Prueba de error en Claude
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_post.side_effect = Exception('API Error')
        with pytest.raises(Exception):
            await generate_claude_response('Test Student')

    # Prueba de error en WhatsApp
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_get.side_effect = Exception('Network Error')
        with pytest.raises(Exception):
            await send_whatsapp_message('+34666777888', 'Test message')


@pytest.mark.asyncio
async def test_service_status_updates(db_session):
    '''Prueba las actualizaciones de estado de servicios.'''
    # Crear un nuevo estado de servicio
    service = ServiceStatus(
        service_name='test_service', status=True, last_check=datetime.utcnow()
    )
    db_session.add(service)
    db_session.commit()

    # Actualizar el estado
    service.status = False
    service.error_message = 'Test error'
    db_session.commit()

    # Verificar la actualización
    updated = (
        db_session.query(ServiceStatus).filter_by(service_name='test_service').first()
    )
    assert not updated.status
    assert updated.error_message == 'Test error'


@pytest.mark.asyncio
async def test_interaction_sensitivity_calculation():
    '''Prueba el cálculo de sensibilidad de las interacciones.'''
    # Probar diferentes escenarios
    test_cases = [
        ('El estudiante está enfermo', 7),
        ('Visita al médico programada', 5),
        ('Emergencia familiar', 9),
        ('Llegará tarde hoy', 3),
    ]

    for message, expected_sensitivity in test_cases:
        with patch('backend.services.claude.generate_claude_response') as mock_claude:
            mock_claude.return_value = {
                'sensitivity': expected_sensitivity,
                'response': 'Test response',
                'likely_to_be_on_leave_tomorrow': False,
                'reach_out_tomorrow': True,
            }

            response = await generate_claude_response(message)
            assert response['sensitivity'] == expected_sensitivity


if __name__ == '__main__':
    pytest.main(['-v', __file__])
