import asyncio
import aiohttp
import json
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from attendance_system.db.models import Interaction
from attendance_system.db.session import SessionLocal
from attendance_system.core.config import settings
from attendance_system.services.claude import generate_claude_response
from attendance_system.services.whatsapp import send_whatsapp_message
import logging

logger = logging.getLogger(__name__)


class AttendanceManager:
    active_connections: dict[int, WebSocket] = {}

    @classmethod
    async def process_whatsapp_message(cls, message_data: dict):
        try:
            student_name = message_data.get("student_name")
            tutor_phone = message_data.get("tutor_phone")

            if not all([student_name, tutor_phone]):
                raise ValueError("Datos incompletos en el mensaje")

            authorized = await cls.verify_authorization(student_name, tutor_phone)
            if not authorized:
                return {"status": "error", "message": "No autorizado"}

            claude_response = await generate_claude_response(student_name)
            await cls.save_interaction(student_name, tutor_phone, claude_response)
            await cls.broadcast_update()

            return {"status": "success", "response": claude_response}

        except Exception as e:
            logger.error(f"Error procesando mensaje de WhatsApp: {str(e)}")
            return {"status": "error", "message": str(e)}

    @classmethod
    async def verify_authorization(cls, student_name: str, tutor_phone: str):
        # Lógica de verificación de autorización aquí
        return True

    @classmethod
    async def save_interaction(
        cls, student_name: str, tutor_phone: str, claude_response: dict
    ):
        session = SessionLocal()
        try:
            interaction = Interaction(
                student_name=student_name,
                tutor_phone=tutor_phone,
                claude_response=claude_response,
                status="active",
            )
            session.add(interaction)
            session.commit()
        finally:
            session.close()

    @classmethod
    async def broadcast_update(cls):
        for connection in cls.active_connections.values():
            try:
                await connection.send_json(
                    {"type": "update", "data": await cls.get_dashboard_data()}
                )
            except Exception as e:
                logger.error(f"Error difundiendo actualización: {str(e)}")

    @classmethod
    async def get_dashboard_data(cls):
        session = SessionLocal()
        try:
            interactions = (
                session.query(Interaction)
                .order_by(Interaction.timestamp.desc())
                .limit(100)
                .all()
            )

            return {
                "service_status": await cls.check_service_status(),
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
        finally:
            session.close()

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
                except:
                    status[service] = False
            return status

    @classmethod
    def add_connection(cls, client_id: int, websocket: WebSocket):
        cls.active_connections[client_id] = websocket

    @classmethod
    def remove_connection(cls, client_id: int):
        if client_id in cls.active_connections:
            del cls.active_connections[client_id]
