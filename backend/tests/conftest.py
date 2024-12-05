import asyncio
import contextlib
import logging
from typing import AsyncGenerator, AsyncContextManager

import async_timeout
import docker
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import asyncio
import contextlib
import logging
from typing import AsyncGenerator, AsyncContextManager

import docker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

# Configuración del logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Agregar el fixture event_loop con scope session
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    print(f"---> event_loop {loop}")
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def postgres_container(event_loop):
    """Proporciona un contenedor PostgreSQL configurado para las pruebas"""
    logger.info("Iniciando fixture del contenedor PostgreSQL")

    # Crear un cliente de Docker
    client = docker.from_env()

    # Configuración del contenedor de PostgreSQL
    container_name = "test-postgres"
    image = "postgres:15"
    username = "test_user"
    password = "test_password"
    dbname = "test_db"
    port = 5432

    # Crear el contenedor
    logger.info("Creando contenedor PostgreSQL")
    container = client.containers.run(
        image=image,
        name=container_name,
        environment={
            "POSTGRES_USER": username,
            "POSTGRES_PASSWORD": password,
            "POSTGRES_DB": dbname
        },
        ports={
            "5432/tcp": port
        },
        detach=True
    )

    # Esperar a que el contenedor esté listo
    logger.info("Esperando a que el contenedor PostgreSQL esté listo")
    while container.status != "running":
        await asyncio.sleep(1)
        container.reload()

    logger.info("Contenedor PostgreSQL iniciado y listo para las pruebas")
    logger.info(f"Contenedor id: {container.id}")
    logger.info(f"Contenedor attrs: {container.attrs}")
    logger.info(f"Contenedor nombre: {container.name}")
    logger.info(f"Contenedor status: {container.status}")

    # Devolver el contenedor
    yield container

    # Detener y eliminar el contenedor
    logger.info("Limpiando fixture del contenedor PostgreSQL")
    container.stop()
    container.remove()
    logger.info("Limpieza del contenedor PostgreSQL completada")

@pytest.fixture(scope="function")
async def db_session(postgres_container: docker.models.containers.Container) -> AsyncGenerator[AsyncSession, None]:
    """Proporciona una sesión de base de datos limpia para cada test"""
    logger = logging.getLogger(__name__)
    logger.debug("Creando nueva sesión de base de datos para test")

    async with _get_session(postgres_container, timeout=120.0) as session:
        yield session
        logger.debug("Limpiando datos después del test")
        await _cleanup_data(postgres_container)

@contextlib.asynccontextmanager
async def _get_session(postgres_container: docker.models.containers.Container, timeout: float = 120.0) -> AsyncGenerator[AsyncSession, None]:
    """Proporciona una sesión de base de datos utilizando el contenedor de PostgreSQL"""
    logger = logging.getLogger(__name__)

    # Obtener la URL de conexión del contenedor
    db_url = f"postgresql://test_user:test_password@{postgres_container.attrs['NetworkSettings']['IPAddress']}:5432/test_db"
    async_url = db_url.replace('postgresql://', 'postgresql+asyncpg://')
    logger.info(f"URL de conexión AsyncPG: {async_url}")

    # Crear el motor y la session factory
    engine = create_async_engine(
        async_url,
        echo=True
    )
    session_factory = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_timeout.timeout(timeout):
        # Proporcionar la sesión
        async with session_factory() as session:
            try:
                yield session
            finally:
                await session.rollback()

async def _cleanup_data(postgres_container: docker.models.containers.Container) -> None:
    """Limpia todos los datos de las tablas en el contenedor de PostgreSQL"""
    logger = logging.getLogger(__name__)
    logger.info("Iniciando limpieza de datos...")

    # Obtener la URL de conexión del contenedor
    db_url = f"postgresql://test_user:test_password@{postgres_container.attrs['NetworkSettings']['IPAddress']}:5432/test_db"
    async_url = db_url.replace('postgresql://', 'postgresql+asyncpg://')
    logger.info(f"URL de conexión AsyncPG: {async_url}")

    # Crear el motor y ejecutar los truncates
    engine = create_async_engine(
        async_url,
        echo=True
    )
    async with engine.begin() as conn:
        tables = [
            'messages',
            'conversations',
            'tutor_student',
            'students',
            'tutors',
            'schools'
        ]
        for table in tables:
            logger.debug(f"Limpiando tabla: {table}")
            await conn.execute(f'TRUNCATE TABLE {table} CASCADE;')

    logger.info("Limpieza de datos completada")