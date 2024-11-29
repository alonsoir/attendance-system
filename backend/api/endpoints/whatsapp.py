"""
WhatsApp Webhook endpoint
"""
import json

from fastapi import APIRouter, Body, HTTPException, requests
from pydantic import BaseModel

from backend.main import app, settings
from backend.services.attendance import AttendanceManager, IncomingMessage, OutgoingMessage

attendance_manager = AttendanceManager.get_instance()
router = APIRouter()


@router.post("/webhook/whatsapp")
async def receive_message_from_tutor_whatsapp_webhook(message_data: dict = Body(...)):
    try:
        # Validar estructura base
        entry = message_data.get("entry", [])
        if not entry:
            raise ValueError("Missing 'entry' in webhook payload")

        changes = entry[0].get("changes", [])
        if not changes:
            raise ValueError("Missing 'changes' in webhook payload")

        value = changes[0].get("value", {})
        contacts = value.get("contacts", [])
        messages = value.get("messages", [])

        if not contacts or not messages:
            raise ValueError("Missing 'contacts' or 'messages' in webhook payload")

        # Extraer información del remitente y mensaje
        contact = contacts[0]
        message = messages[0]

        sender_name = contact.get("profile", {}).get("name", "Unknown")
        sender_phone = contact.get("wa_id", "").strip()
        if not sender_phone:
            raise ValueError("Sender phone (wa_id) is missing or invalid")

        message_content = message.get("text", {}).get("body", "").strip()
        if not message_content:
            raise ValueError("Message content is missing")

        timestamp = message.get("timestamp", "").strip()
        if not timestamp:
            raise ValueError("Timestamp is missing")

        # Procesar datos
        processed_data : IncomingMessage= {
            "sender_phone": sender_phone,
            "sender_name": sender_name,
            "message_content": message_content,
            "timestamp": timestamp,
        }

        return await attendance_manager.process_whatsapp_message_from_tutor_to_claude(processed_data)

    except Exception as e:
        # Manejar errores y enviar una respuesta informativa
        return {"error": f"Failed to process message: {str(e)}"}

# Configuración
ACCESS_TOKEN = settings.WHATSAPP_META_API_KEY

class WhatsAppMessage(BaseModel):
    recipient_phone_number: str
    message_text: str

@app.post("/send-whatsapp-message/")
async def send_whatsapp_message(message: WhatsAppMessage):
    try:
        # URL de la API de WhatsApp de Meta
        url = 'https://graph.facebook.com/v16.0/me/messages'

        # Cabeceras
        headers = {
            'Authorization': f'Bearer {ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }

        # Cuerpo del mensaje
        outgoing_message = OutgoingMessage(
            messaging_product="whatsapp",
            to=message.recipient_phone_number,
            type="text",
            body=message.message_text
        )

        # Enviar el mensaje
        response = requests.post(url, headers=headers, data=json.dumps(outgoing_message.to_dict()))

        # Verificar la respuesta
        if response.status_code == 200:
            return {"status": "success", "message": "Mensaje enviado con éxito"}
        else:
            raise HTTPException(status_code=response.status_code, detail=response.json())

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/v1/whatsapp/send")
async def send_message_to_whatsapp_webhook_from_college_to_tutor(
    message_data: dict = Body(...),
):
    """
    message_data = {
        "messaging_product": "whatsapp",
        "to": "recipient_phone_number",  # Número de teléfono del destinatario en formato internacional
        "type": "text",
        "text": {
            "body": "message_text"  # Contenido del mensaje
        }
    }
    """
    return await attendance_manager.process_whatsapp_message_from_college_to_tutor(message_data)
