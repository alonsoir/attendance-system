import logging

import aiohttp
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from starlette.websockets import WebSocket

from backend.db.models import Interaction
from backend.db.session import get_db
from backend.services.claude import generate_claude_response

logger = logging.getLogger(__name__)


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

    import logging

    # En el método `process_whatsapp_message`, agrega logs para verificar el flujo.
    logging.basicConfig(level=logging.DEBUG)

    async def process_whatsapp_message(self, message_data: dict):
        """Process incoming WhatsApp messages."""
        try:
            student_name = message_data.get("student_name")
            tutor_phone = message_data.get("tutor_phone")

            # Validaciones en orden correcto
            if student_name is None:
                raise ValueError("null_name")
            if not student_name:  # Esto captura strings vacíos
                raise ValueError("empty_name")
            if len(student_name) > 100:
                raise ValueError("name_too_long")
            if not tutor_phone or len(tutor_phone) < 10:
                raise ValueError("invalid_phone")

            authorized = await self.verify_authorization(student_name, tutor_phone)
            if not authorized:
                return {"status": "error", "message": "Unauthorized access"}

            claude_response = await generate_claude_response(student_name)

            async with get_db() as session:
                try:
                    interaction = Interaction(
                        student_name=student_name,
                        tutor_phone=tutor_phone,
                        claude_response=claude_response,
                        status="active",
                    )
                    session.add(interaction)
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    logger.error(f"Database error during interaction save: {str(e)}")
                    return {"status": "error", "message": f"Database error: {str(e)}"}

            try:
                await self.broadcast_update()
            except Exception as e:
                logger.error(f"Error during broadcast: {str(e)}")

            return {"status": "success", "response": claude_response}

        except ValueError as ve:
            # Re-lanzar las excepciones de validación
            logger.error(f"Validation error: {str(ve)}")
            raise
        except Exception as e:
            logger.error(f"General error processing WhatsApp message: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def verify_authorization(self, student_name: str, tutor_phone: str):
        """
        Verifies if the student is authorized for the operation.
        """
        # TODO Placeholder for real authorization logic
        logger.info(f"Verifying authorization for {student_name} with tutor_phone {tutor_phone}")
        return True

    async def save_interaction(self, db_session, student_name: str, tutor_phone: str, claude_response: dict):
        """
        Saves the interaction to the database.
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
        Sends updates to all connected clients.
        """
        if not self.active_connections:
            logger.debug("No active connections to broadcast to")
            return

        dashboard_data = await self.get_dashboard_data()
        update_message = {
            "type": "update",
            "data": dashboard_data
        }

        disconnected_clients = []

        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_json(update_message)
                logger.debug(f"Successfully sent update to client {client_id}")
            except Exception as e:
                logger.error(f"Error broadcasting update to client {client_id}: {str(e)}")
                disconnected_clients.append(client_id)

        # Limpiar conexiones muertas
        for client_id in disconnected_clients:
            logger.info(f"Removing disconnected client {client_id}")
            self.active_connections.pop(client_id, None)

    async def get_dashboard_data(self):
        """
        Retrieves dashboard data.
        """
        logger.debug("Entering get_dashboard_data")
        try:
            logger.debug("Fetching service status")
            service_status = await self.check_service_status()
            logger.debug(f"Service status: {service_status}")

            logger.debug("Starting database session")
            async with get_db() as db_session:
                try:
                    logger.debug("Executing database query")
                    result = await db_session.execute(
                        select(Interaction).order_by(Interaction.timestamp.desc()).limit(100)
                    )
                    logger.debug("Getting scalars from result")
                    scalars_result = result.scalars()
                    logger.debug("Getting all from scalars")
                    interactions = scalars_result.all()
                    logger.debug(f"Found {len(interactions)} interactions")

                    formatted_interactions = [
                        {
                            "id": i.id,
                            "timestamp": i.timestamp.isoformat(),
                            "student_name": i.student_name,
                            "status": i.status,
                            "claude_response": i.claude_response,
                        }
                        for i in interactions
                    ]
                    logger.debug(f"Formatted {len(formatted_interactions)} interactions")

                    response = {
                        "service_status": service_status,
                        "interactions": formatted_interactions,
                    }
                    logger.debug("Successfully prepared response")
                    return response

                except SQLAlchemyError as e:
                    logger.error(f"Database error while fetching dashboard data: {str(e)}")
                    return {"service_status": service_status, "interactions": []}
                except Exception as e:
                    logger.error(f"Unexpected error in database operations: {str(e)}")
                    return {"service_status": service_status, "interactions": []}
        except Exception as e:
            logger.error(f"Error fetching dashboard data: {str(e)}")
            return {"service_status": {}, "interactions": []}

    @classmethod
    async def check_service_status(cls):
        """
        Verifies the status of external services.
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
        Adds a new client connection.
        """
        self.active_connections[client_id] = websocket

    def remove_connection(self, client_id: int):
        """
        Removes an existing client connection.
        """
        self.active_connections.pop(client_id, None)
