import logging
import aiohttp
from starlette.websockets import WebSocket
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select

from backend.db.models import Interaction
from backend.db.session import get_db
from backend.services.claude import generate_claude_response

logger = logging.getLogger(__name__)


class AttendanceManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """Singleton Pattern - Asegura una única instancia de la clase."""
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return  # Evitar re-inicializar Singleton
        self.active_connections = {}
        self.__initialized = True

    @staticmethod
    def get_instance():
        """Método estático para obtener la instancia única."""
        if not AttendanceManager._instance:
            AttendanceManager()
        return AttendanceManager._instance

    async def process_whatsapp_message(self, message_data: dict):
        """
        Procesa un mensaje recibido de WhatsApp y responde con datos generados.
        """
        try:
            student_name = message_data.get("student_name")
            tutor_phone = message_data.get("tutor_phone")

            if not all([student_name, tutor_phone]):
                raise ValueError("Incomplete data. Both 'student_name' and 'tutor_phone' are required.")

            authorized = await self.verify_authorization(student_name, tutor_phone)
            if not authorized:
                return {"status": "error", "message": "Unauthorized access"}

            claude_response = await generate_claude_response(student_name)
            async with get_db() as db_session:
                await self.save_interaction(db_session, student_name, tutor_phone, claude_response)

            await self.broadcast_update()
            return {"status": "success", "response": claude_response}

        except Exception as e:
            logger.error(f"Error processing WhatsApp message: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def verify_authorization(student_name: str, tutor_phone: str):
        """
        Verifica si el estudiante está autorizado para realizar la operación.
        """
        # TODO Placeholder para lógica real de autorización
        logger.info(f"Verifying authorization for {student_name} with tutor_phone {tutor_phone}")
        return True

    async def save_interaction(db_session, student_name: str, tutor_phone: str, claude_response: dict):
        """
        Guarda la interacción en la base de datos.
        """
        try:
            interaction = Interaction(
                student_name=student_name,
                tutor_phone=tutor_phone,
                claude_response=claude_response,
                status="active",
            )
            db_session.add(interaction)
            await db_session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Database error while saving interaction: {str(e)}")
            await db_session.rollback()
            raise

    async def broadcast_update(self):
        """
        Envía actualizaciones a todos los clientes conectados.
        """
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_json(
                    {"type": "update", "data": await self.get_dashboard_data()}
                )
            except Exception as e:
                logger.error(f"Error broadcasting update to client {client_id}: {str(e)}")

    async def get_dashboard_data(self):
        """
        Recupera los datos del dashboard.
        """
        async with get_db() as db_session:
            try:
                result = await db_session.execute(
                    select(Interaction).order_by(Interaction.timestamp.desc()).limit(100)
                )
                interactions = result.scalars().all()

                return {
                    "service_status": await self.check_service_status(),
                    "interactions": [
                        {
                            "id": i.id,
                            "timestamp": i.timestamp.isoformat(),
                            "student_name": i.student_name,
                            "status": i.status,
                            "claude_response": i.claude_response,
                        }
                        for i in interactions
                    ],
                }
            except SQLAlchemyError as e:
                logger.error(f"Database error while fetching dashboard data: {str(e)}")
                return {"service_status": {}, "interactions": []}

    async def check_service_status(self):
        """
        Verifica el estado de los servicios externos.
        """
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

    def add_connection(self, client_id: int, websocket: WebSocket):
        """
        Añade una nueva conexión de cliente.
        """
        self.active_connections[client_id] = websocket

    def remove_connection(self, client_id: int):
        """
        Elimina una conexión de cliente existente.
        """
        self.active_connections.pop(client_id, None)
