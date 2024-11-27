from asyncio.log import logger

from sqlalchemy import select

from backend.db.models import ServiceStatus
from backend.db.session import get_db


# Modificar para utilizar las funciones asincrónicas
async def check_service_status(service_name: str) -> bool:
    """Check if a service is available asynchronously."""
    async with get_db() as db:
        try:
            # Usar `scalars().first()` para obtener el resultado asincrónicamente
            status = await db.execute(
                select(ServiceStatus).filter_by(service_name=service_name)
            )
            result = await status.scalars().first()
            return result.status if result else False
        except Exception as e:
            # Puedes registrar un error aquí si es necesario
            logger.error(
                f"Error al verificar el estado del servicio {service_name}: {e}"
            )
            return False
