import asyncio
import contextlib
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

import async_timeout
import bcrypt
import docker
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from backend.db.models_acl import User

logger = logging.getLogger(__name__)

# Configuración del logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Constantes
CONTAINER_NAME = "test-postgres-full-citus"
IMAGE = "test-postgres-full-citus"  # Usar la imagen personalizada
USERNAME = "test_user"
PASSWORD = "test_password"
DBNAME = "test_db"


def get_container_by_partial_name(client, partial_name: str):
    """
    Busca un contenedor cuyo nombre contenga un prefijo específico.
    Args:
        client: Cliente de Docker.
        partial_name: Subcadena esperada en el nombre del contenedor.
    Returns:
        docker.models.containers.Container: Contenedor encontrado.
    Raises:
        docker.errors.NotFound: Si no se encuentra un contenedor.
    """
    logger.info(f"Buscando contenedor con nombre parcial: '{partial_name}'")
    containers = client.containers.list(all=True)
    for container in containers:
        if partial_name in container.name:
            logger.info(f"Contenedor encontrado: {container.name}")
            return container
    raise docker.errors.NotFound(
        f"No se encontró contenedor con nombre parcial '{partial_name}'"
    )


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    print(f"---> event_loop {loop}")
    yield loop
    print("---> Cerrando event_loop")  # Añadimos log para verificar que se ejecuta
    # Asegurarnos de que todas las tareas pendientes se completen
    pending = asyncio.all_tasks(loop)
    loop.run_until_complete(asyncio.gather(*pending))
    loop.close()


import socket


def is_port_in_use(port: int) -> bool:
    """
    Verifica si un puerto específico está en uso
    Args:
        port: Número de puerto a verificar
    Returns:
        bool: True si el puerto está en uso, False en caso contrario
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Setting SO_REUSEADDR before bind allows the socket to be bound
            # even if it's in a TIME_WAIT state
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("127.0.0.1", port))
            return False
    except socket.error:
        return True


def get_free_port() -> int:
    """
    Encuentra un puerto disponible
    Returns:
        int: Número de puerto disponible
    Raises:
        RuntimeError: Si no se puede encontrar un puerto disponible
    """
    logger.info("Buscando puerto disponible")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))  # Bind to port 0 lets OS pick a free port
            s.listen(1)
            port = s.getsockname()[1]
            logger.info(f"Puerto disponible encontrado: {port}")
            return port
    except Exception as e:
        logger.error(f"Error al buscar puerto disponible: {str(e)}")
        raise RuntimeError(f"No se pudo encontrar un puerto disponible: {str(e)}")


def _generate_encrypt_key() -> str:
    """Genera una clave de cifrado segura"""
    return os.urandom(32).decode("utf-8")


def _hash_password(password: str) -> str:
    """Hashea una contraseña utilizando bcrypt"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


async def _get_admin_role_id(session: AsyncSession) -> str:
    """Obtiene el ID del rol de administrador"""
    result = await session.execute(text("SELECT id FROM roles WHERE name = 'ADMIN'"))
    return result.scalar()


async def _get_school_role_id(session: AsyncSession) -> str:
    """Obtiene el ID del rol de escuela"""
    result = await session.execute(text("SELECT id FROM roles WHERE name = 'SCHOOL'"))
    return result.scalar()


async def _get_tutor_role_id(session: AsyncSession) -> str:
    """Obtiene el ID del rol de tutor"""
    result = await session.execute(text("SELECT id FROM roles WHERE name = 'TUTOR'"))
    return result.scalar()


@pytest.fixture(scope="session")
async def postgres_container(event_loop):
    """Proporciona un contenedor PostgreSQL configurado para las pruebas"""
    logger.info("=== INICIO postgres_container fixture ===")
    container = None
    client = docker.from_env()
    port = get_free_port()
    logger.info(f"Puerto asignado para PostgreSQL: {port}")

    try:
        # Limpieza de contenedor existente
        try:
            existing = get_container_by_partial_name(client, CONTAINER_NAME)
            logger.info(
                f"Encontrado contenedor existente {existing.name}. Eliminándolo..."
            )
            await _remove_container(existing)
            logger.info(f"Contenedor existente {CONTAINER_NAME} eliminado")
        except docker.errors.NotFound:
            logger.info(
                f"No se encontró contenedor existente con nombre parcial {CONTAINER_NAME}"
            )

        # Crear nuevo contenedor
        container = client.containers.run(
            image=IMAGE,
            name=CONTAINER_NAME,
            environment={
                "POSTGRES_USER": USERNAME,
                "POSTGRES_PASSWORD": PASSWORD,
                "POSTGRES_DB": DBNAME,
            },
            ports={"5432/tcp": ("127.0.0.1", port)},
            detach=True,
            remove=True,
        )

        logger.info(f"Contenedor creado: {container.id}")

        # Esperar a que PostgreSQL esté listo
        logger.info("Esperando a que PostgreSQL esté listo...")
        await _wait_for_postgres(container, port)

        # Obtener la clave de encriptación generada por el contenedor
        encrypt_key = await _get_encryption_key(container, port)

        yield container, port, encrypt_key

    finally:
        if container:
            logger.info("=== Iniciando limpieza final ===")
            await _remove_container(container)
            logger.info("=== Limpieza completada ===")


async def _get_encryption_key(container, port):
    """Obtiene la clave de encriptación generada por el contenedor"""
    async with _get_session(container, port) as session:
        result = await session.execute(
            text("SELECT key_value FROM encryption_config WHERE key_name = 'main_key'")
        )
        key = result.scalar()
        return key


async def _wait_for_postgres(container, port):
    max_attempts = 30
    attempt = 0

    port_bindings = container.attrs["NetworkSettings"]["Ports"]
    logger.info(f"Configuración de puertos: {port_bindings}")

    async def try_connect():
        conn_str = (
            f"postgresql+asyncpg://{USERNAME}:{PASSWORD}@127.0.0.1:{port}/{DBNAME}"
        )
        engine = create_async_engine(conn_str)
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            return True

    while attempt < max_attempts:
        try:
            await try_connect()
            logger.info("Conexión exitosa a PostgreSQL")
            return
        except Exception as e:
            logger.error(f"Intento {attempt + 1} fallido: {str(e)}")
            attempt += 1
            await asyncio.sleep(2)  # Aumentar el tiempo entre intentos

        if attempt % 5 == 0:
            container.reload()
            logger.info(f"Estado del contenedor: {container.status}")
            logs = container.logs().decode("utf-8")
            logger.info(f"Últimos logs:\n{logs}")

    raise TimeoutError("PostgreSQL no está disponible después de 30 intentos")


async def _load_schema(
    container: docker.models.containers.Container, port: int
) -> None:
    """Carga el esquema de la base de datos"""
    logger.info("Cargando esquema de la base de datos...")
    schema_path = (
        Path(__file__).resolve().parent.parent / "db" / "schema" / "init_database.sh"
    )

    if not schema_path.exists():
        logger.error(f"Archivo de esquema no encontrado en {schema_path}")
        raise FileNotFoundError(f"Archivo de esquema no encontrado en {schema_path}")

    async with _get_session(container, port, timeout=480.0) as session:
        logger.info("Ejecutando script de inicialización de la base de datos...")
        await session.execute(text(schema_path.read_text()))
        await session.commit()
        logger.info("Esquema de base de datos cargado exitosamente")


@asynccontextmanager
async def _get_session(
    container: docker.models.containers.Container, port: int, timeout: float = 480.0
) -> AsyncGenerator[AsyncSession, None]:
    """Proporciona una sesión de base de datos utilizando el contenedor de PostgreSQL"""
    logger.info("Creando sesión de base de datos")

    db_url = _get_db_url(container, port)
    engine = create_async_engine(db_url, echo=True)
    session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with async_timeout.timeout(timeout):
            logger.info("Iniciando conexión con timeout de %s segundos", timeout)
            async with session_factory() as session:
                logger.info("Conexión establecida exitosamente")
                yield session
    except Exception as e:
        logger.error(f"Error al conectar: {str(e)}")
        logger.error(f"Tipo de error: {type(e)}")
        raise


def _get_db_url(container: docker.models.containers.Container, port: int) -> str:
    """Obtiene la URL de conexión a la base de datos"""
    return f"postgresql+asyncpg://{USERNAME}:{PASSWORD}@127.0.0.1:{port}/{DBNAME}"


async def _load_test_data(
    container: docker.models.containers.Container, port: int
) -> None:
    """Carga datos iniciales de prueba"""
    logger.info("=== Iniciando carga de datos de prueba ===")

    async with _get_session(container, port) as session:
        try:
            # Crear usuarios de prueba
            admin_user = User(
                username="admin",
                password_hash=_hash_password("admin_password"),
                role_id=await _get_admin_role_id(session),
            )
            school_user = User(
                username="school_user",
                password_hash=_hash_password("school_password"),
                role_id=await _get_school_role_id(session),
            )
            tutor_user = User(
                username="tutor_user",
                password_hash=_hash_password("tutor_password"),
                role_id=await _get_tutor_role_id(session),
            )
            session.add_all([admin_user, school_user, tutor_user])
            await session.commit()

            logger.info("Datos de prueba cargados exitosamente")

        except Exception as e:
            logger.error(f"Error cargando datos de prueba: {e}")
            raise


async def _remove_container(container, retries=3):
    """Helper function to remove a container with retries"""
    for attempt in range(retries):
        try:
            await asyncio.sleep(1)  # Pequeña pausa antes de intentar eliminar
            container.stop()
            container.remove(force=True)
            return True
        except Exception as e:
            if attempt == retries - 1:  # Último intento
                logger.error(
                    f"No se pudo eliminar el contenedor después de {retries} intentos: {e}"
                )
                return False
            logger.warning(f"Intento {attempt + 1} fallido al eliminar contenedor: {e}")
            await asyncio.sleep(1)  # Esperar antes del siguiente intento


from backend.services.database_manager import DatabaseManager
from backend.tests.test_settings import TestSettings


@pytest.fixture(scope="function")
async def db_session(postgres_container) -> AsyncGenerator[DatabaseManager, None]:
    container, port, encrypt_key = postgres_container
    logger.info("=== INICIO db_session fixture ===")

    # Crear configuración de prueba
    test_settings = TestSettings(
        POSTGRES_USER=USERNAME,
        POSTGRES_PASSWORD=PASSWORD,
        POSTGRES_DB=DBNAME,
        POSTGRES_PORT=port,
        POSTGRES_SERVER="localhost",
    )

    db_manager = DatabaseManager.get_instance(settings=test_settings)
    await db_manager.connect(encrypt_key)

    try:
        yield db_manager
    finally:
        await db_manager.disconnect()
        logger.info("=== FIN db_session fixture ===")


@pytest.fixture(scope="function")
async def admin_user(db_session: DatabaseManager) -> User:
    return await db_session.get_user("admin")


@pytest.fixture(scope="function")
async def school_user(db_session: DatabaseManager) -> User:
    return await db_session.get_user("school_user")


@pytest.fixture(scope="function")
async def tutor_user(db_session: DatabaseManager) -> User:
    return await db_session.get_user("tutor_user")


@pytest.fixture(scope="function", autouse=True)
async def cleanup_after_test(postgres_container):
    """Limpia la base de datos después de cada test de stored procedures"""
    logger.info("=== INICIO cleanup_after_test para stored procedures ===")
    logger.info(f"Estado inicial del container: {postgres_container[0].status}")

    yield  # Esto ocurre antes del test

    try:
        logger.info("=== Ejecutando limpieza post-test de stored procedures ===")
        container, port, encrypt_key = postgres_container

        # Obtener logs del contenedor
        logs = container.logs().decode("utf-8")
        logger.info(f"Logs del contenedor durante el test:\n{logs}")

        # Verificar estado del contenedor
        container.reload()
        logger.info(f"Estado final del container: {container.status}")

        # Mostrar información de la base de datos
        logger.info(f"Puerto usado: {port}")
        logger.info(f"Encrypt key presente: {'Si' if encrypt_key else 'No'}")

    except Exception as e:
        logger.error(f"Error durante la limpieza de stored procedures: {e}")
        logger.error(f"Traza completa:", exc_info=True)
    finally:
        logger.info("=== FIN cleanup_after_test de stored procedures ===")
