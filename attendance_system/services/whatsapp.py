import asyncio
import aiohttp
import json
from attendance_system.core.config import settings
import logging

from attendance_system.services import AttendanceManager

logger = logging.getLogger(__name__)


async def send_whatsapp_message(phone: str, message: str):
    url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={message}&apikey={settings.META_API_KEY}"
    logger.info(f"Enviando mensaje a {phone}: {message}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
    except Exception as e:
        logger.error(f"Error al enviar mensaje: {str(e)}")


async def handle_whatsapp_message(message_data: dict):
    try:
        student_name = message_data.get('student_name')
        tutor_phone = message_data.get('tutor_phone')

        if not all([student_name, tutor_phone]):
            raise ValueError("Datos incompletos en el mensaje")

        # Llamar al servicio de gestión de ausencias para procesar el mensaje
        result = await AttendanceManager.process_whatsapp_message(message_data)

        # Enviar respuesta de vuelta a WhatsApp
        if result["status"] == "success":
            await send_whatsapp_message(tutor_phone, result["response"])

        return result

    except Exception as e:
        logger.error(f"Error procesando mensaje de WhatsApp: {str(e)}")
        return {"status": "error", "message": str(e)}