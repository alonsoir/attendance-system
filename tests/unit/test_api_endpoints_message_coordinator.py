# Tests para backend/api/endpoints/message_coordinator.py
import pytest
from unittest.mock import patch, AsyncMock
from fastapi import status
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.message_coordinator import MessageCoordinator, MessageData


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.asyncio
@patch("app.services.message_coordinator.MessageCoordinator._validate_phone_number")
@patch("app.services.attendance.AttendanceManager.process_whatsapp_message")
async def test_whatsapp_webhook(mock_process_whatsapp, mock_validate_phone, client):
    """Prueba el endpoint del webhook de WhatsApp."""
    mock_validate_phone.return_value = True
    mock_process_whatsapp.return_value = {
        "status": "success",
        "response": "Mensaje procesado",
    }

    message_data = {
        "student_name": "John Doe",
        "tutor_phone": "+34612345678",
        "message_content": "Hello, world!",
    }
    response = await client.post("/api/v1/webhook/whatsapp", json=message_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    assert data["response"] == "Mensaje procesado"
    mock_validate_phone.assert_called_once_with(message_data["tutor_phone"])
    mock_process_whatsapp.assert_called_once_with(message_data)


@patch("app.services.message_coordinator.MessageCoordinator._validate_phone_number")
async def test_whatsapp_webhook_invalid_phone(mock_validate_phone, client):
    """Prueba el webhook de WhatsApp con número de teléfono inválido."""
    mock_validate_phone.return_value = False

    message_data = {
        "student_name": "John Doe",
        "tutor_phone": "invalid_phone",
        "message_content": "Hello, world!",
    }
    response = await client.post("/api/v1/webhook/whatsapp", json=message_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert data["status"] == "error"
    assert "Invalid phone number format" in data["message"]
    mock_validate_phone.assert_called_once_with(message_data["tutor_phone"])


@patch("app.services.message_coordinator.MessageCoordinator._validate_message_data")
async def test_whatsapp_webhook_invalid_data(mock_validate_data, client):
    """Prueba el webhook de WhatsApp con datos inválidos."""
    mock_validate_data.side_effect = ValueError("student_name is required")

    message_data = {"tutor_phone": "+34612345678", "message_content": "Hello, world!"}
    response = await client.post("/api/v1/webhook/whatsapp", json=message_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert data["status"] == "error"
    assert "student_name is required" in data["message"]
    mock_validate_data.assert_called_once_with(message_data)


@patch("app.services.message_coordinator.MessageCoordinator._validate_message_data")
@patch("app.services.message_coordinator.MessageCoordinator.send_response")
async def test_whatsapp_webhook_send_response_error(
    mock_send_response, mock_validate_data, client
):
    """Prueba el webhook de WhatsApp cuando hay un error al enviar la respuesta."""
    mock_validate_data.return_value = MessageData(
        student_name="John Doe",
        tutor_phone="+34612345678",
        message_content="Hello, world!",
    )
    mock_send_response.side_effect = Exception("Network error")

    message_data = {
        "student_name": "John Doe",
        "tutor_phone": "+34612345678",
        "message_content": "Hello, world!",
    }
    response = await client.post("/api/v1/webhook/whatsapp", json=message_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "error"
    assert "warning" in data
    assert "error_details" in data
    mock_validate_data.assert_called_once_with(message_data)
    mock_send_response.assert_called_once_with(
        "+34612345678", "Message processed successfully"
    )
