import logging
from datetime import datetime
from typing import Dict, Any, Callable

logger = logging.getLogger(__name__)


async def process_message(
        message_data: dict,
        send_response_callback: Callable
) -> Dict[str, Any]:
    """
    Coordina el procesamiento de mensajes y el envío de respuestas.
    """
    try:
        student_name = message_data.get("student_name")
        tutor_phone = message_data.get("tutor_phone")

        if not all([student_name, tutor_phone]):
            raise ValueError("Datos incompletos en el mensaje")

        # Importación local para evitar ciclos
        from backend.services.attendance import AttendanceManager

        # Procesar el mensaje
        result = await AttendanceManager.process_whatsapp_message(message_data)

        # Enviar respuesta si es exitoso
        if result["status"] == "success":
            try:
                await send_response_callback(tutor_phone, result["response"])
            except Exception as e:
                logger.error(f"Error sending response: {str(e)}")
                result["warning"] = "Message processed but response delivery failed"

        return result

    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": str(datetime.now()),
        }