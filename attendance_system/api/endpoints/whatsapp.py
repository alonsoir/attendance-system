from fastapi import APIRouter, Body
from attendance_system.services.whatsapp import handle_whatsapp_message
from attendance_system.core.config import settings

router = APIRouter()

@router.post("/webhook/whatsapp")
async def whatsapp_webhook(message_data: dict = Body(...)):
    return await handle_whatsapp_message(message_data)