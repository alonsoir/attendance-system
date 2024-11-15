from fastapi import APIRouter, Body

from backend.core.config import settings
from backend.services.whatsapp import handle_whatsapp_message

router = APIRouter()


@router.post("/webhook/whatsapp")
async def whatsapp_webhook(message_data: dict = Body(...)):
    return await handle_whatsapp_message(message_data)
