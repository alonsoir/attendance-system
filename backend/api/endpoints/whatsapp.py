"""
WhatsApp Webhook endpoint
"""
from fastapi import APIRouter, Body

from backend.services.attendance import AttendanceManager

attendance_manager = AttendanceManager()
router = APIRouter()

@router.post("/webhook/whatsapp")
async def whatsapp_webhook(message_data: dict = Body(...)):
    return await attendance_manager.process_whatsapp_message(message_data)

