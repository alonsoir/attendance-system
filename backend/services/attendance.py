import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

import aiohttp
from starlette.websockets import WebSocket

from backend.core import get_settings
from backend.services.claude import ClaudeService
from backend.services.utils import PhoneNumberValidator
from backend.services.whatsapp import MessageProvider, WhatsAppService

logger = logging.getLogger(__name__)


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


from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class OutgoingMessage:
    """Estructura de datos para mensajes salientes de WhatsApp"""

    messaging_product: str
    to: str
    type: str
    body: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "messaging_product": self.messaging_product,
            "to": self.to,
            "type": self.type,
            "text": {"body": self.body},
        }


@dataclass
class MessageData:
    """Estructura de datos para validar mensajes entrantes y salientes entre Claude, WhatsApp y la BD"""

    id: Optional[int]
    student_name: str
    tutor_phone: str
    college_phone: str
    college_name: str
    message_content: str
    tutor_name: str
    sensitivity: int
    likely_to_be_on_leave_tomorrow: bool
    reach_out_tomorrow: bool
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
            "sensitivity": self.sensitivity,
            "likely_to_be_on_leave_tomorrow": self.likely_to_be_on_leave_tomorrow,
            "reach_out_tomorrow": self.reach_out_tomorrow,
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
        self, incomingMessage: IncomingMessage
    ) -> Dict[str, Any]:
        """
        Queremos enviar la respuesta del tutor a Claude para que genere una respuesta.
        """
        try:
            # Validar y procesar el mensaje
            validated_data = self._validate_incoming_message_data(incomingMessage)
            logger.info(f"Processing message for student: {validated_data.sender_name}")

            response: dict = self._send_message_to_claude_from_tutor(validated_data)
            print(response)
            # Preparar datos para guardar en la base de datos
            data_from_tutor_to_be_saved: MessageData = MessageData(
                id=None,
                student_name=validated_data.sender_name,
                tutor_phone=validated_data.sender_phone,
                college_phone=validated_data.sender_phone,  # Asumiendo que el tutor y el colegio tienen el mismo número
                college_name="College Name",  # Asumiendo un nombre de colegio genérico
                message_content=validated_data.message_content,
                tutor_name=validated_data.sender_name,
                sensitivity=None,  # lo recojo de Claude, en el response anterior.
                likely_to_be_on_leave_tomorrow=None,  # lo recojo de Claude, en el response anterior.
                reach_out_tomorrow=None,  # lo recojo de Claude, en el response anterior.
                timestamp=validated_data.timestamp,
            )

            # Guardar la interacción en la base de datos, probablemente usando un ORM como SQLAlchemy
            # necesitaré que el motor genere el id de la interacción y actualizar el objeto data_from_tutor_to_be_saved
            # con el id generado. TODO implementar esta lógica. Necesitas que la conversacion esté alineada entre el
            #  tutor el colegio con los mensajes de Claude en medio.
            await self._save_interaction_to_db(data_from_tutor_to_be_saved)

            return {
                "status": "success",
                "response": "Message processed successfully",
                "message_data": data_from_tutor_to_be_saved,
            }

        except ValueError as e:
            # Re-lanzar las excepciones de validación
            logger.error(f"Validation error: {str(e)}")
            raise ValueError(f"Validation failed: {str(e)}")
        except Exception as e:
            logger.error(f"Network or processing error: {str(e)}", exc_info=True)
            raise Exception(f"Processing error: {str(e)}")

    async def process_whatsapp_message_from_college_to_tutor(
        self, outgoingMessage: OutgoingMessage
    ) -> Dict[str, Any]:
        try:
            # Validar y procesar el mensaje
            validated_data: OutgoingMessage = self._validate_outgoing_message_data(
                outgoingMessage
            )
            logger.info(
                f"Processing message for tutor: {validated_data.to} "
                f"with content: {validated_data.body}"
            )

            # Crear MessageData para el envío
            message_data_to_send = MessageData(
                id=None,
                student_name="Estudiante",
                tutor_phone=validated_data.to,
                college_phone="college_phone",
                college_name="College Name",
                message_content=validated_data.body,
                tutor_name="Tutor",
                sensitivity=5,  # valor por defecto
                likely_to_be_on_leave_tomorrow=False,  # valor por defecto
                reach_out_tomorrow=False,  # valor por defecto
                timestamp=datetime.now(),
            )

            # Enviar mensaje al tutor
            response = await self._send_message_to_tutor_From_Claude(
                message_data_to_send
            )

            # Guardar la interacción en la base de datos
            await self._save_interaction_to_db(response)

            return {"status": "success", "response": "Message processed successfully"}

        except ValueError as e:
            # Manejar las excepciones de validación retornando un error en lugar de relanzarlas
            logger.error(f"Validation error: {str(e)}")
            return {
                "status": "error",
                "message": f"Processing failed: {str(e)}",
                "error_type": "ValueError",
            }
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

    def _validate_incoming_message_data(
        self, incoming: IncomingMessage
    ) -> IncomingMessage:
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

    def _validate_outgoing_message_data(
        self, outgoing: OutgoingMessage
    ) -> OutgoingMessage:
        """
        Valida y convierte los datos del mensaje.
        Args:
            outgoing (OutgoingMessage): Objeto que contiene los datos del mensaje entrante.
            Returns:
            OutgoingMessage: El objeto de mensaje entrante validado.
        Raises:
            ValueError: Si se detectan errores en los datos.
        """
        errors = []

        messaging_product = outgoing.messaging_product
        if not messaging_product:
            errors.append("messaging_product is required")
        to = outgoing.to
        to_validated = PhoneNumberValidator.validate_phone(to)
        if not to:
            errors.append("to is required")
        if not to_validated:
            errors.append("to is invalid")
        type = outgoing.type
        if not type:
            errors.append("type is required")
        body = outgoing.body
        if not body:
            errors.append("body is required")
        if errors:
            raise ValueError(f"Validation errors: {errors}")
        return outgoing

    async def _receive_message_from_tutor(
        self, validated_data: IncomingMessage
    ) -> Dict[str, Any]:
        """
        Simula la recepción de un mensaje de un tutor.
        """
        logger.info(f"Received message from tutor: {validated_data}")
        settings = get_settings()
        # settings.print_settings()
        service = WhatsAppService(
            provider=settings.WHATSAPP_PROVIDER,
            meta_api_key=settings.WHATSAPP_META_API_KEY,
            callback_token=settings.WHATSAPP_CALLBACK_TOKEN,
        )
        await service.initialize()

        response: Dict[str, Any] = await service.get_message_from_tutor(
            validated_data.to_dict()
        )
        logger.info(response)
        return response

    def _build_message(self, validated_data: MessageData) -> str:
        is_final_message = (
            validated_data.likely_to_be_on_leave_tomorrow
            and validated_data.reach_out_tomorrow
        )

        base_message = (
            f"Hola, {validated_data.college_name}. Soy Attendance Manager, nos ha contactado el tutor "
            f"{validated_data.tutor_name} sobre el estudiante {validated_data.student_name}. "
            f"El tutor nos ha proporcionado los siguientes datos: {validated_data.message_content}"
        )

        if is_final_message:
            return (
                f"{base_message}\n\n"
                f"Según la información proporcionada, el estudiante se reincorporará a las clases mañana. "
                f"Este será el último mensaje de seguimiento para este caso. Si necesitan información adicional, "
                f"por favor, inicien una nueva consulta."
            )

        return base_message

    async def _send_message_to_college_from_Claude(
        self, validated_data: MessageData
    ) -> MessageData:
        """
             El envío de un mensaje whatsapp a un colegio. Tengo que ser capaz de saber si es el mensaje final o no.
             En la respuesta recibo siempre esta estructura:
             {
        "sensitivity": <integer between 1-10>,
        "response": <your empathetic response>,
        "likely_to_be_on_leave_tomorrow": <boolean>,
        "reach_out_tomorrow": <boolean>,
        "conversation_id": <string> # ID único para la conversación
             }
             Si likely_to_be_on_leave_tomorrow y reach_out_tomorrow son True, entonces el mensaje desde Claude es el último.
        """
        message = self._build_message(validated_data)
        logger.info(f"Sending message to college: {message}")
        settings = get_settings()
        # settings.print_settings()
        service = WhatsAppService(
            provider=settings.WHATSAPP_PROVIDER,
            meta_api_key=settings.WHATSAPP_META_API_KEY,
            callback_token=settings.WHATSAPP_CALLBACK_TOKEN,
        )
        await service.initialize()
        response: Dict[str, Any] = await service.send_message(
            validated_data.tutor_phone, message
        )
        print(response)
        return response

    async def _send_message_to_claude_from_tutor(self, validated_data: IncomingMessage):
        """
        El envío de un mensaje a Claude. Tengo que ser capaz de saber si es el mensaje final o no.
        :param validated_data:
        :return:
        """
        message = (
            f"Hi Claude, el tutor {validated_data.sender_name} has sent the following message: "
            f"{validated_data.message_content}. Please provide a response to this message."
        )

        # Tengo que enviar un mensaje a Claude de parte del tutor!!!!
        service = ClaudeService.get_instance()
        service.initialize()
        response: Dict[str, Any] = await service.generate_response_when_tutor(message)
        return response

    async def _send_message_to_tutor_From_Claude(
        self, validated_data: MessageData
    ) -> MessageData:
        message = (
            f"Hola, {validated_data.tutor_name}. Soy Attendance Manager, nos ha contactado el colegio "
            f"{validated_data.college_name} solicitando información sobre el estudiante "
            f"{validated_data.student_name}. ¿Puedes proporcionarnos el estado actual de "
            f"{validated_data.student_name}?"
        )

        settings = get_settings()
        # Configuración del servicio

        service = WhatsAppService(
            provider=MessageProvider.META,
            meta_api_key=settings.WHATSAPP_META_API_KEY,
            callback_token=settings.WHATSAPP_CALLBACK_TOKEN,
        )
        service.initialize()  # Inicializar el cliente HTTP

        logger.info(f"Sending message to tutor: {validated_data.tutor_phone}")
        response: Dict[str, Any] = await service.send_message(
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
