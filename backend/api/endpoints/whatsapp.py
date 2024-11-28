"""
WhatsApp Webhook endpoint
"""
from fastapi import APIRouter, Body

from backend.services.attendance import AttendanceManager

attendance_manager = AttendanceManager()
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
        processed_data = {
            "sender_phone": sender_phone,
            "sender_name": sender_name,
            "message_content": message_content,
            "timestamp": timestamp,
        }

        return await attendance_manager.process_whatsapp_message_from_tutor_to_claude(processed_data)

    except Exception as e:
        # Manejar errores y enviar una respuesta informativa
        return {"error": f"Failed to process message: {str(e)}"}


@router.post("/api/v1/whatsapp/send")
async def send_message_to_whatsapp_webhook_from_college_to_tutor(
    message_data: dict = Body(...),
):
    return await attendance_manager.process_whatsapp_message_from_college_to_tutor(
        message_data
    )
