import logging
from contextlib import asynccontextmanager

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()
# Construir la DATABASE_URI desde el archivo .env
DATABASE_URI = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"


# Crear el motor asincrónico
def create_engine(db_uri: str):
    return create_async_engine(db_uri, echo=True)


async_engine = create_engine(DATABASE_URI)
# Crear el fabricante de sesiones asincrónicas
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

logger.info("Database engine initialized successfully.")


# Contexto asíncrono para manejar sesiones de base de datos
@asynccontextmanager
async def get_db():
    """
    Contexto para manejar sesiones de base de datos de manera asíncrona.
    Asegura que la sesión se cierre después de su uso.
    """
    async with AsyncSessionLocal() as db:
        yield db


# Versión asincrónica de get_db para dependencias FastAPI
async def get_db_context():
    """
    Versión sin decorador del get_db para uso en dependencias FastAPI.
    """
    async with AsyncSessionLocal() as db:
        yield db


# Verificación asincrónica de la conexión a la base de datos
async def check_database_connection():
    """
    Verifica la conexión a la base de datos.
    """
    try:
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Error conectando a la base de datos: {str(e)}")
        return False


# Inicialización de la base de datos con datos predeterminados
async def init_db():
    """
    Inicializa la base de datos con datos iniciales si es necesario.
    """
    from backend.db.models import ServiceStatus, User

    async with AsyncSessionLocal() as db:  # Usa 'async with' para crear una sesión asincrónica
        try:
            # Verificar si ya existen registros de estado de servicio
            result_claude = await db.execute(
                select(ServiceStatus).filter(ServiceStatus.service_name == "claude")
            )
            service_status_claude = await result_claude.scalars().first()

            result_meta = await db.execute(
                select(ServiceStatus).filter(ServiceStatus.service_name == "meta")
            )
            service_status_meta = await result_meta.scalars().first()

            if not service_status_claude and not service_status_meta:
                services = [
                    ServiceStatus(service_name="claude", status=True),
                    ServiceStatus(service_name="meta", status=True),
                ]
                db.add_all(services)
                await db.commit()
                logger.info("Estados de servicio iniciales creados")
        except Exception as e:
            logger.error(f"Error inicializando la base de datos: {str(e)}")
            await db.rollback()  # Esto es necesario?
        finally:
            await db.close()  # Esto es necesario?
