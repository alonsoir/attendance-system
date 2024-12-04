import pytest
import asyncio
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from .containers.postgres import PostgresTestContainer

# Configuración del logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session"""
    logger = logging.getLogger(__name__)
    logger.info("Creando event loop para la sesión de pruebas")
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    logger.info("Cerrando event loop de la sesión de pruebas")
    loop.close()


@pytest.fixture(scope="session")
async def postgres_container():
    """Proporciona un contenedor PostgreSQL configurado para las pruebas"""
    logger = logging.getLogger(__name__)
    logger.info("Iniciando fixture del contenedor PostgreSQL")

    container = PostgresTestContainer()
    await container.start()
    logger.info("Contenedor PostgreSQL iniciado y listo para las pruebas")

    yield container

    logger.info("Limpiando fixture del contenedor PostgreSQL")
    await container.stop()
    logger.info("Limpieza del contenedor PostgreSQL completada")


@pytest.fixture(async_def=True)
async def db_session(postgres_container: PostgresTestContainer) -> AsyncGenerator[AsyncSession, None]:
    """Proporciona una sesión de base de datos limpia para cada test"""
    logger = logging.getLogger(__name__)
    logger.debug("Creando nueva sesión de base de datos para test")

    async for session in postgres_container.get_session():
        yield session
        logger.debug("Limpiando datos después del test")
        await postgres_container.cleanup_data()