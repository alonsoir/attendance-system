import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any

import aiohttp
from starlette.websockets import WebSocket

from backend.core import get_settings
from backend.services.claude import ClaudeService
from backend.services.utils import PhoneNumberValidator
from backend.services.whatsapp import WhatsAppService

logger = logging.getLogger(__name__)

""""
"status": "success",
                "phone": phone_number,
                "message": message,
                "provider": "meta",
                "timestamp": str(datetime.now()),
"""
@dataclass
class IncomingMessage:
    """Estructura de datos para mensajes entrantes de WhatsApp"""
    sender_phone: str
    sender_name: str
    message_content: str
    timestamp: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sender_phone": self.sender_phone,
            "sender_name": self.sender_name,
            "message_content": self.message_content,
            "timestamp": self.timestamp,
        }
@dataclass
class MessageData:
    """Estructura de datos para validar mensajes entrantes y salientes entre Claude, WhatsApp y la BD"""

    id: int
    student_name: str
    tutor_phone: str
    college_phone: str
    college_name: str
    message_content: str = ""
    tutor_name: str = ""
    timestamp: datetime = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "student_name": self.student_name,
            "tutor_phone": self.tutor_phone,
            "college_phone": self.college_phone,
            "college_name": self.college_name,
            "message_content": self.message_content,
            "tutor_name": self.tutor_name,
            "timestamp": self.timestamp,
        }

    def get(self, param, param1):
        return self.get(param, param1)


class AttendanceManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """Singleton Pattern - Ensures a single instance of the class."""
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return  # Prevent re-initializing Singleton
        self.active_connections = {}
        self.__initialized = True

    @staticmethod
    def get_instance():
        """Static method to retrieve the unique instance."""
        if not AttendanceManager._instance:
            AttendanceManager()
        return AttendanceManager._instance

    async def process_whatsapp_message_from_tutor_to_claude(
            self, message_data: IncomingMessage
    ) -> Dict[str, Any]:
        try:
            # Validar y procesar el mensaje
            validated_data: IncomingMessage = self._validate_incoming_message_data(message_data)
            logger.info(
                f"Processing message for student: {validated_data.sender_name}"
            )
            response: Dict[str, Any] = await self._receive_message_from_tutor(validated_data)

            # Guardar la interacción en la base de datos, quien asigna el id? la base de datos?
            data_from_tutor_to_be_saved: MessageData = MessageData(
                # id=validated_data.id,
                student_name=validated_data.sender_name,
                tutor_phone=validated_data.sender_phone,
                college_phone=validated_data.sender_phone,  # Asumiendo que el tutor y el colegio tienen el mismo número
                college_name="College Name",  # Asumiendo un nombre de colegio genérico
                message_content=response["message"],
                tutor_name=validated_data.sender_name,
                timestamp=datetime.now(),
            )
            # Guardar la interacción en la base de datos
            await self._save_interaction_to_db(data_from_tutor_to_be_saved)

            return {"status": "success", "response": "Message processed successfully"}

        except ValueError as e:
            # Re-lanzar las excepciones de validación
            logger.error(f"Validation error: {str(e)}")
            raise ValueError("Validation failed")
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "message": f"Processing failed: {str(e)}",
                "error_type": e.__class__.__name__,
            }

    async def process_whatsapp_message_from_college_to_tutor(
        self, message_data: dict
    ) -> Dict[str, Any]:
        try:
            # Validar y procesar el mensaje
            validated_data = self._validate_message_data(message_data)
            logger.info(
                f"Processing message for tutor: {validated_data.tutor_name} "
                f"from college: {validated_data.college_name}"
            )

            # Enviar mensaje al tutor
            response: MessageData = await self._send_message_to_tutor(validated_data)

            # Guardar la interacción en la base de datos. id lo genera la base de datos
            await self._save_interaction_to_db(response)

            # Esperar respuesta del tutor
            # tutor_response = await self._wait_for_tutor_response(validated_data)

            # Generar PDF con la conversación completa
            # await self._generate_pdf_report(validated_data, tutor_response)

            # Enviar PDF al colegio
            # await self._send_report_to_college(validated_data.college_phone)

            return {"status": "success", "response": "Message processed successfully"}

        except ValueError as e:
            # Re-lanzar las excepciones de validación
            logger.error(f"Validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "message": f"Processing failed: {str(e)}",
                "error_type": e.__class__.__name__,
            }

    def _validate_phone_number(self, phone: str) -> bool:

        return PhoneNumberValidator.validate_phone(phone)

    def _validate_college_name(self, college_name: str) -> bool:
        """Valida el nombre del colegio"""
        return True

    def _validate_incoming_message_data(self, incoming: IncomingMessage) -> IncomingMessage:
        """
        Valida y convierte los datos del mensaje.

        Args:
            incoming (IncomingMessage): Objeto que contiene los datos del mensaje entrante.

        Returns:
            IncomingMessage: El objeto de mensaje entrante validado.

        Raises:
            ValueError: Si se detectan errores en los datos.
        """
        errors = []

        # Validar sender_phone
        sender_phone = incoming.sender_phone.strip()
        if not sender_phone:
            errors.append("sender_phone is required")
        elif not PhoneNumberValidator.validate_phone(sender_phone):
            errors.append("Invalid sender_phone number format")

        # Validar sender_name
        sender_name = incoming.sender_name.strip()
        if not sender_name:
            errors.append("sender_name is required")

        # Validar message_content
        message_content = incoming.message_content.strip()
        if not message_content:
            errors.append("message_content is required")

        # Validar timestamp
        timestamp = incoming.timestamp
        if not isinstance(timestamp, int) or timestamp <= 0:
            errors.append("timestamp is invalid or required")

        if errors:
            raise ValueError(f"Validation errors: {errors}")

        return incoming

    def _validate_message_data(self, message_data: MessageData) -> MessageData:
        """Valida y convierte los datos del mensaje."""
        errors = []
        id = message_data.get("id", "")
        if not id:
            errors.append("id is required")
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

        college_name = message_data.get("college_name", "").strip()
        if not college_name:
            errors.append("college_name is required")
        elif not self._validate_college_name(college_phone):
            errors.append("Invalid college name number format")

        message_content = message_data.get("message_content", "").strip()
        if not message_content:
            errors.append("message_content is required")

        if errors:
            raise ValueError(f"Message validation failed: {', '.join(errors)}")

        return MessageData(
            id=id,
            student_name=student_name,
            tutor_phone=tutor_phone,
            college_phone=college_phone,
            college_name=college_name,
            message_content=message_content,
            tutor_name=message_data.get("tutor_name", "").strip(),
            timestamp=datetime.now(),
        )

    async def _receive_message_from_tutor(self, validated_data: IncomingMessage) -> Dict[str, Any]:
        """
        Simula la recepción de un mensaje de un tutor.
        """
        logger.info(f"Received message from tutor: {validated_data}")
        settings = get_settings()
        settings.print_settings()
        service = WhatsAppService(
            provider=settings.WHATSAPP_PROVIDER,
            meta_api_key=settings.WHATSAPP_META_API_KEY,
            callback_token=settings.WHATSAPP_CALLBACK_TOKEN,
        )
        await service.init_service()

        response: Dict[str, Any] = service.get_message_from_tutor(validated_data.to_dict())
        logger.info(response)
        return response

    async def _send_message_to_tutor(self, validated_data: MessageData) -> MessageData:
        message = (
            f"Hola, {validated_data.tutor_name}. Soy Attendance Manager, nos ha contactado el colegio "
            f"{validated_data.college_name} solicitando información sobre el estudiante "
            f"{validated_data.student_name}. ¿Puedes proporcionarnos el estado actual de "
            f"{validated_data.student_name}?"
        )
        """
        response is a dictionary with the following keys:
        {
            "status": "success",
            "mock": True,
            "phone": phone,
            "message": message,
            "provider": "mock",
            "response": message,
            "timestamp": str(datetime.now()),
        }
        """

        response: Dict[str, Any] = await WhatsAppService.get_instance().send_message(
            validated_data.tutor_phone, message
        )
        print(response)
        return response

    async def _save_interaction_to_db(
        self, data_to_be_saved_from_tutor: MessageData
    ) -> None:
        """Guarda la interacción en la base de datos."""
        logger.info(f"Saving data to database: {data_to_be_saved_from_tutor}")
        logger.warning(f"NOT IMPLEMENTED YET")
        pass

    async def _wait_for_tutor_response(
        self, validated_data: MessageData
    ) -> Dict[str, Any]:
        tutor_response = await ClaudeService.get_instance().wait_for_tutor_response(
            validated_data.student_name, validated_data.tutor_phone
        )

        # Guardar la respuesta del tutor en la base de datos

        return tutor_response

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
        # Lógica para enviar el PDF al colegio
        await WhatsAppService.get_instance().send_message(
            college_phone, "Adjunto encontrará el reporte de la conversación."
        )

    async def broadcast_update(self, client_id: int, websocket: WebSocket):
        if not self.active_connections:
            logger.debug("No active connections to broadcast to")
            return

        dashboard_data = await self.get_dashboard_data()
        update_message = {"type": "update", "data": dashboard_data}

        disconnected_clients = []

        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_json(update_message)
                logger.debug(f"Successfully sent update to client {client_id}")
            except Exception as e:
                logger.error(
                    f"Error broadcasting update to client {client_id}: {str(e)}"
                )
                disconnected_clients.append(client_id)

        # Limpiar conexiones muertas
        for client_id in disconnected_clients:
            logger.info(f"Removing disconnected client {client_id}")
            self.active_connections.pop(client_id, None)

    def add_connection(self, client_id: int, websocket: WebSocket):
        self.active_connections[client_id] = websocket

    def remove_connection(self, client_id: int):
        self.active_connections.pop(client_id, None)

    @classmethod
    async def check_service_status(cls):
        async with aiohttp.ClientSession() as session:
            services = {
                "claude": "https://status.anthropic.com",
                "meta": "https://developers.facebook.com/status/dashboard/",
            }
            status = {}
            for service, url in services.items():
                try:
                    async with session.get(url) as response:
                        status[service] = response.status == 200
                except Exception:
                    status[service] = False
        return status

    async def cleanup(self):
        logger.info("Cleaning up AttendanceManager resources...")
