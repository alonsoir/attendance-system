import logging
import asyncio
from datetime import datetime
from typing import Any, Callable, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MessageData:
    """Estructura de datos para validar mensajes entrantes."""
    student_name: str
    tutor_phone: str
    message_content: str = ""
    tutor_name: str = ""
    timestamp: datetime = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "student_name": self.student_name,
            "tutor_phone": self.tutor_phone,
            "message_content": self.message_content,
            "tutor_name": self.tutor_name,
            "timestamp": self.timestamp
        }


class MessageCoordinator:
    _instance: Optional["MessageCoordinator"] = None
    _lock: asyncio.Lock
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MessageCoordinator, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._lock = asyncio.Lock()
            self._initialized = True
            logger.info("MessageCoordinator initialized")

    @classmethod
    def get_instance(cls) -> "MessageCoordinator":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _validate_phone_number(self, phone: str) -> bool:
        """Valida formato básico de número de teléfono para España y Estados Unidos."""
        import re
        # Patrones específicos por país:
        # España: +34 seguido de 6,7,8,9 y 8 dígitos más
        # USA: +1 seguido de 10 dígitos
        phone_pattern = r'^\+34[6789]\d{8}$|^\+1\d{10}$'
        return bool(re.match(phone_pattern, phone))

    def _validate_message_data(self, message_data: dict) -> MessageData:
        """Valida y convierte los datos del mensaje."""
        errors = []

        student_name = message_data.get("student_name", "").strip()
        if not student_name:
            errors.append("student_name is required")

        tutor_phone = message_data.get("tutor_phone", "").strip()
        if not tutor_phone:
            errors.append("tutor_phone is required")
        elif not self._validate_phone_number(tutor_phone):
            errors.append("Invalid phone number format")

        if errors:
            raise ValueError(f"Message validation failed: {', '.join(errors)}")

        return MessageData(
            student_name=student_name,
            tutor_phone=tutor_phone,
            message_content=message_data.get("message_content", "").strip(),
            tutor_name=message_data.get("tutor_name", "").strip(),
            timestamp=datetime.now()
        )

    async def process_message(
            self,
            message_data: dict,
            send_response_callback: Callable
    ) -> Dict[str, Any]:
        """
        Coordina el procesamiento de mensajes y el envío de respuestas.

        Args:
            message_data: Diccionario con los datos del mensaje
            send_response_callback: Función callback para enviar respuestas

        Returns:
            Dict con el resultado del procesamiento

        Raises:
            ValueError: Si los datos del mensaje son inválidos
        """
        async with self._lock:
            try:
                # Validar datos del mensaje
                validated_data = self._validate_message_data(message_data)
                logger.info(f"Processing message for student: {validated_data.student_name}")

                # Importación local para evitar ciclos
                from backend.services.attendance import AttendanceManager

                # Procesar el mensaje
                result = await AttendanceManager.process_whatsapp_message(
                    validated_data.to_dict()
                )

                # Enviar respuesta si es exitoso
                if result.get("status") == "success":
                    try:
                        await send_response_callback(
                            validated_data.tutor_phone,
                            result.get("response", "Message processed successfully")
                        )
                    except Exception as e:
                        logger.error(f"Error sending response: {str(e)}")
                        result["warning"] = "Message processed but response delivery failed"
                        result["error_details"] = str(e)

                # Añadir metadata al resultado
                result.update({
                    "timestamp": str(validated_data.timestamp),
                    "processing_completed": True
                })

                return result

            except ValueError as e:
                logger.error(f"Validation error: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Validation failed: {str(e)}",
                    "timestamp": str(datetime.now())
                }
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}", exc_info=True)
                return {
                    "status": "error",
                    "message": f"Processing failed: {str(e)}",
                    "timestamp": str(datetime.now()),
                    "error_type": e.__class__.__name__
                }

    async def cleanup(self):
        """Limpia recursos si es necesario."""
        logger.info("Cleaning up MessageCoordinator resources...")
        # Implementar limpieza de recursos si es necesario


# Instancia global
message_coordinator = MessageCoordinator.get_instance()