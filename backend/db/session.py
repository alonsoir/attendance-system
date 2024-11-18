import logging
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from backend.core.config import settings  # Asegúrate de tener los parámetros del .env aquí

logger = logging.getLogger(__name__)

# Construir la DATABASE_URI desde el archivo .env
DATABASE_URI = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

# Crear el motor asincrónico
engine = create_async_engine(DATABASE_URI, echo=True)

# Crear el fabricante de sesiones asincrónicas
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Contexto asíncrono para manejar sesiones de base de datos
@asynccontextmanager
async def get_db():
    """
    Contexto para manejar sesiones de base de datos de manera asíncrona.
    Asegura que la sesión se cierre después de su uso.
    """
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()


# Versión asincrónica de get_db para dependencias FastAPI
async def get_db_context():
    """
    Versión sin decorador del get_db para uso en dependencias FastAPI.
    """
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()


# Verificación asincrónica de la conexión a la base de datos
async def check_database_connection():
    """
    Verifica la conexión a la base de datos.
    """
    try:
        async with AsyncSessionLocal() as db:
            await db.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Error conectando a la base de datos: {str(e)}")
        return False


# Inicialización de la base de datos con datos predeterminados
async def init_db():
    '''
    Inicializa la base de datos con datos iniciales si es necesario.
    '''
    from backend.db.models import ServiceStatus, User

    async with AsyncSessionLocal() as db:  # Usa 'async with' para crear una sesión asincrónica
        try:
            # Verificar si ya existen registros de estado de servicio
            service_status = await db.execute(select(ServiceStatus)).scalars().first()
            if not service_status:
                services = [
                    ServiceStatus(service_name="claude", status=True),
                    ServiceStatus(service_name="meta", status=True),
                ]
                db.add_all(services)
                await db.commit()
                logger.info("Estados de servicio iniciales creados")
        except Exception as e:
            logger.error(f"Error inicializando la base de datos: {str(e)}")
            await db.rollback()
        finally:
            await db.close()
