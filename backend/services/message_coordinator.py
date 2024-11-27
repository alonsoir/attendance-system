import logging
import asyncio
from datetime import datetime
from typing import Any, Dict, Optional
from dataclasses import dataclass

from .whatsapp_manager import WhatsappManager
from .attendance_manager import AttendanceManager
from .claude_manager import ClaudeManager
from .database_manager import DatabaseManager

logger = logging.getLogger(__name__)


@dataclass
class MessageData:
    """Estructura de datos para validar mensajes entrantes."""

    student_name: str
    tutor_phone: str
    college_phone: str
    message_content: str = ""
    tutor_name: str = ""
    timestamp: datetime = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "student_name": self.student_name,
            "tutor_phone": self.tutor_phone,
            "college_phone": self.college_phone,
            "message_content": self.message_content,
            "tutor_name": self.tutor_name,
            "timestamp": self.timestamp,
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

        phone_pattern = r"^\+34[6789]\d{8}$|^\+1\d{10}$"
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
            errors.append("Invalid tutor phone number format")

        college_phone = message_data.get("college_phone", "").strip()
        if not college_phone:
            errors.append("college_phone is required")
        elif not self._validate_phone_number(college_phone):
            errors.append("Invalid college phone number format")

        message_content = message_data.get("message_content", "").strip()
        if not message_content:
            errors.append("message_content is required")

        if errors:
            raise ValueError(f"Message validation failed: {', '.join(errors)}")

        return MessageData(
            student_name=student_name,
            tutor_phone=tutor_phone,
            college_phone=college_phone,
            message_content=message_content,
            tutor_name=message_data.get("tutor_name", "").strip(),
            timestamp=datetime.now(),
        )

    async def process_message(self, message_data: dict) -> Dict[str, Any]:
        """
        Coordina el procesamiento de mensajes, incluyendo envío de mensajes al tutor y guardado en base de datos.

        Args:
            message_data: Diccionario con los datos del mensaje

        Returns:
            Dict con el resultado del procesamiento

        Raises:
            ValueError: Si los datos del mensaje son inválidos
        """
        async with self._lock:
            try:
                # Validar datos del mensaje
                validated_data = self._validate_message_data(message_data)
                logger.info(
                    f"Processing message for student: {validated_data.student_name}"
                )

                # Enviar mensaje al tutor
                await self._send_message_to_tutor(validated_data)

                # Guardar la interacción en la base de datos
                await self._save_interaction_to_db(validated_data)

                return {"status": "success", "response": "Message sent to tutor"}

            except ValueError as e:
                logger.error(f"Validation error: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Validation failed: {str(e)}",
                    "timestamp": str(datetime.now()),
                }
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}", exc_info=True)
                return {
                    "status": "error",
                    "message": f"Processing failed: {str(e)}",
                    "timestamp": str(datetime.now()),
                    "error_type": e.__class__.__name__,
                }

    async def wait_for_tutor_response(
        self, validated_data: MessageData
    ) -> Dict[str, Any]:
        """Espera la respuesta del tutor de manera asíncrona."""
        # Lógica para esperar y recibir la respuesta del tutor
        tutor_response = await ClaudeManager.get_instance().wait_for_tutor_response(
            validated_data.student_name, validated_data.tutor_phone
        )

        # Guardar la respuesta del tutor en la base de datos
        await DatabaseManager.get_instance().save_tutor_response(
            student_name=validated_data.student_name,
            tutor_phone=validated_data.tutor_phone,
            tutor_response=tutor_response["message"],
            timestamp=tutor_response["timestamp"],
        )

        return tutor_response

    async def _send_message_to_tutor(self, validated_data: MessageData) -> None:
        """Envía un mensaje al tutor solicitando información."""
        message = f"Hola, {validated_data.tutor_name}. Soy Attendance Manager, nos ha contactado el colegio {validated_data.message_content} solicitando información sobre el estudiante {validated_data.student_name}. ¿Puedes proporcionarnos el estado actual de {validated_data.student_name}?"
        await WhatsappManager.get_instance().send_message(
            validated_data.tutor_phone, message
        )

    async def _save_interaction_to_db(self, validated_data: MessageData) -> None:
        """Guarda la interacción entre Claude y el tutor en la base de datos."""
        await DatabaseManager.get_instance().save_interaction(
            student_name=validated_data.student_name,
            tutor_phone=validated_data.tutor_phone,
            college_phone=validated_data.college_phone,
            message_content=validated_data.message_content,
            tutor_name=validated_data.tutor_name,
            timestamp=validated_data.timestamp,
        )

    async def _generate_pdf_report(
        self, validated_data: MessageData, tutor_response: Dict[str, Any]
    ) -> None:
        """Genera un PDF con la conversación completa."""
        # Lógica para generar el PDF con la conversación
        pdf_content = (
            f"Estudiante: {validated_data.student_name}\n"
            f"Colegio: {validated_data.message_content}\n"
            f"Tutor: {validated_data.tutor_name} ({validated_data.tutor_phone})\n"
            f"Mensaje inicial: {validated_data.message_content}\n"
            f"Respuesta del tutor: {tutor_response['message']}\n"
            f"Timestamp: {tutor_response['timestamp']}"
        )
        await AttendanceManager.get_instance().save_pdf_report(
            validated_data.student_name, pdf_content
        )

    async def _send_report_to_college(self, college_phone: str) -> None:
        """Envía el PDF con la conversación al colegio."""
        # Lógica para enviar el PDF al colegio
        await WhatsappManager.get_instance().send_message(
            college_phone, "Adjunto encontrará el reporte de la conversación."
        )

    async def cleanup(self):
        """Limpia recursos si es necesario."""
        logger.info("Cleaning up MessageCoordinator resources...")
        # Implementar limpieza de recursos si es necesario


# Instancia global
message_coordinator = MessageCoordinator.get_instance()
