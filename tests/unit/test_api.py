import pytest
from fastapi import status


def test_health_check(client):
    '''Prueba el endpoint de health check.'''
    response = client.get('/health')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'status' in data
    assert 'timestamp' in data
    assert 'version' in data
    assert 'services' in data

def test_whatsapp_webhook(client, mock_whatsapp_message):
    '''Prueba el endpoint del webhook de WhatsApp.'''
    response = client.post('/api/v1/webhook/whatsapp', json=mock_whatsapp_message)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['status'] == 'success'
    assert 'response' in data


def test_whatsapp_webhook_invalid_data(client):
    '''Prueba el webhook de WhatsApp con datos inválidos.'''
    response = client.post('/api/v1/webhook/whatsapp', json={'invalid': 'data'})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_websocket_connection(client):
    '''Prueba la conexión WebSocket.'''
    with client.websocket_connect('/api/v1/ws') as websocket:
        data = websocket.receive_json()
        assert 'type' in data
        assert data['type'] == 'connection_established'


def test_get_interactions(client, test_interaction):
    '''Prueba la obtención de interacciones.'''
    response = client.get('/api/v1/interactions')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data['items'], list)
    assert len(data['items']) > 0
    assert data['total'] > 0


def test_get_interaction_detail(client, test_interaction):
    """Prueba la obtención del detalle de una interacción."""
    response = client.get(f'/api/v1/interactions/{test_interaction["id"]}')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['student_name'] == test_interaction['student_name']
    assert data['tutor_phone'] == test_interaction['tutor_phone']


def test_update_interaction(client, test_interaction):
    '''Prueba la actualización de una interacción.'''
    update_data = {'status': 'resolved', 'sensitivity_score': 3}
    response = client.patch(
        f'/api/v1/interactions/{test_interaction["id"]}', json=update_data
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['status'] == 'resolved'
    assert data['sensitivity_score'] == 3


def test_service_status(client, mock_service_status):
    '''Prueba la obtención del estado de los servicios.'''
    response = client.get('/api/v1/services/status')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'claude' in data
    assert 'meta' in data


@pytest.mark.asyncio
async def test_websocket_updates(client, test_interaction):
    '''Prueba las actualizaciones en tiempo real vía WebSocket.'''
    with client.websocket_connect('/api/v1/ws') as websocket:
        # Actualizar una interacción
        update_data = {'status': 'resolved'}
        response = client.patch(
            f'/api/v1/interactions/{test_interaction["id"]}', json=update_data
        )
        assert response.status_code == status.HTTP_200_OK

        # Verificar que recibimos la actualización
        data = websocket.receive_json()
        assert data['type'] == 'update'
        assert 'data' in data


def test_metrics_endpoint(client):
    '''Prueba el endpoint de métricas.'''
    response = client.get('/metrics')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, dict)


def test_error_handling(client):
    '''Prueba el manejo de errores.'''
    response = client.get('/api/v1/nonexistent')
    assert response.status_code == status.HTTP_404_NOT_FOUND

    response = client.post('/api/v1/interactions', json={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
