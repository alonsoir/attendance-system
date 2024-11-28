"""
WhatsApp Webhook endpoint
"""
from fastapi import APIRouter, Body

from backend.services.attendance import AttendanceManager

attendance_manager = AttendanceManager()
router = APIRouter()


@router.post("/webhook/whatsapp")
async def receive_message_from_tutor_whatsapp_webhook(message_data: dict = Body(...)):
    return await attendance_manager.process_whatsapp_message_from_tutor_to_claude(
        message_data
    )


@router.post("/api/v1/whatsapp/send")
async def send_message_to_whatsapp_webhook_from_college_to_tutor(
    message_data: dict = Body(...),
):
    return await attendance_manager.process_whatsapp_message_from_college_to_tutor(
        message_data
    )
