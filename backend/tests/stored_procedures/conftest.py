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
from backend.services.database_manager import DatabaseManager
from backend.tests.test_settings import TestSettings

logger = logging.getLogger(__name__)

# Configuración del logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Constantes
CONTAINER_NAME = "attendance_system-coordinator-1"
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
    client = docker.from_env()

    try:
        container = get_container_by_partial_name(client, CONTAINER_NAME)
        logger.info(f"Usando contenedor existente: {container.name}")

        # Reiniciar el contenedor
        logger.info("Reiniciando contenedor...")
        container.restart()
        await asyncio.sleep(5)

        # Verificar el estado después del reinicio
        container.reload()
        logger.info(f"Estado del contenedor: {container.status}")

        # Configurar PostgreSQL
        commands = [
            'echo "listen_addresses = \'*\'" >> /var/lib/postgresql/data/postgresql.conf',
            'echo "host all all 0.0.0.0/0 trust" >> /var/lib/postgresql/data/pg_hba.conf'
        ]

        for cmd in commands:
            result = container.exec_run(['bash', '-c', cmd])
            logger.info(f"Ejecutando: {cmd}")
            logger.info(f"Resultado: {result.output.decode('utf-8')}")

        # Recargar configuración
        result = container.exec_run('su postgres -c "pg_ctl reload -D /var/lib/postgresql/data"')
        logger.info(f"Recargando PostgreSQL: {result.output.decode('utf-8')}")

        # Esperar a que esté listo
        await _wait_for_postgres(container)

        # Obtener la clave de encriptación
        encrypt_key = await _get_encryption_key(container)
        logger.info(f"Clave obtenida y decodificada: {len(encrypt_key)} bytes")

        yield container, 5432, encrypt_key

    except Exception as e:
        logger.error(f"Error al configurar el contenedor: {str(e)}")
        raise


async def _wait_for_postgres(container, max_retries=5, retry_delay=2):
    """Espera a que PostgreSQL esté listo para aceptar conexiones"""
    import asyncpg
    import asyncio
    from asyncio import open_connection

    for attempt in range(max_retries):
        try:
            # Primero verificar la conectividad TCP
            logger.info("Verificando conectividad TCP...")
            reader, writer = await asyncio.wait_for(
                open_connection('127.0.0.1', 5432),
                timeout=5
            )
            writer.close()
            await writer.wait_closed()
            logger.info("Conexión TCP exitosa")

            # Si TCP funciona, intentar conexión PostgreSQL
            dsn = f"postgresql://{USERNAME}:{PASSWORD}@127.0.0.1:5432/{DBNAME}"
            logger.info(f"Intentando conexión con DSN: {dsn}")

            conn = await asyncpg.connect(
                dsn,
                timeout=10,
                command_timeout=10
            )

            version = await conn.fetchval('SELECT version()')
            logger.info(f"Conexión exitosa. Versión: {version}")

            await conn.close()
            return True

        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Intento {attempt + 1} fallido: {type(e).__name__}: {str(e)}")
                await asyncio.sleep(retry_delay)
            else:
                logger.error(f"No se pudo conectar después de {max_retries} intentos")
                raise TimeoutError("PostgreSQL no está disponible") from e


import base64


async def _get_encryption_key(container):
    """Obtiene la clave de encriptación del contenedor y la decodifica de base64"""
    logger.info("Obteniendo clave de encriptación...")

    # Obtener la clave en formato base64
    result = container.exec_run(
        'psql -U test_user -d test_db -t -A -c "SELECT key_value FROM encryption_config WHERE key_name = \'main_key\';"'
    )

    key_b64 = result.output.decode('utf-8').strip()
    logger.info(f"Clave en base64: {key_b64}")

    if key_b64:
        try:
            # Decodificar la clave desde base64 y mantenerla como bytes
            key_bytes = base64.b64decode(key_b64)
            logger.info(f"Longitud de la clave decodificada: {len(key_bytes)} bytes")
            # Verificar que la clave se puede encodear de nuevo correctamente
            key_b64_check = base64.b64encode(key_bytes).decode('utf-8')
            logger.info(f"Clave re-encoded para verificación: {key_b64_check}")
            if key_b64_check != key_b64:
                logger.error("¡Error! La clave no coincide después de encode/decode!")
            return key_bytes
        except Exception as e:
            logger.error(f"Error al decodificar la clave: {e}")
            raise
    else:
        logger.warning("No se encontró la clave de encriptación")
        return None


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


@pytest.fixture(scope="function")
async def db_session(postgres_container) -> AsyncGenerator[DatabaseManager, None]:
    """Fixture para proveer una sesión de base de datos"""
    container, port, encrypt_key = postgres_container
    logger.info("=== INICIO db_session fixture ===")

    # Verificar la implementación de encriptación
    await _check_encryption_implementation(container)

    # Probar las funciones de encriptación
    await _test_encryption(container)

    # Important: La clave ya viene en bytes, no la convertimos
    logger.info(f"Clave recibida en base64: {base64.b64encode(encrypt_key).decode('utf-8')}")

    # Crear configuración de prueba
    test_settings = TestSettings(
        POSTGRES_USER=USERNAME,
        POSTGRES_PASSWORD=PASSWORD,
        POSTGRES_DB=DBNAME,
        POSTGRES_PORT=port,
        POSTGRES_SERVER="localhost",
    )

    # Reiniciar el singleton para asegurar un estado limpio
    DatabaseManager.reset_instance()

    # Crear una nueva instancia con la clave
    db_manager = DatabaseManager.get_instance(settings=test_settings, encrypt_key=encrypt_key)
    await db_manager.connect()

    try:
        logger.info(
            f"Verificando clave en DatabaseManager: {base64.b64encode(db_manager.encrypt_key).decode('utf-8') if db_manager.encrypt_key else None}")
        yield db_manager
    finally:
        await db_manager.disconnect()
        logger.info("=== FIN db_session fixture ===")


async def _check_encryption_implementation(container):
    """Verifica la implementación de la encriptación en la base de datos"""
    logger.info("Verificando implementación de encriptación...")

    commands = [
        # Ver la función de encriptación
        'psql -U test_user -d test_db -c "\df+ encrypt_value"',
        # Ver la función de desencriptación
        'psql -U test_user -d test_db -c "\df+ decrypt_value"',
        # Ver un ejemplo de datos encriptados
        'psql -U test_user -d test_db -c "SELECT username, convert_from(decode(username, \'base64\'), \'UTF8\') as decoded FROM users LIMIT 1;"',
        # Ver la definición de la función decrypt_value
        'psql -U test_user -d test_db -c "SELECT pg_get_functiondef(\'decrypt_value\'::regproc);"',
        # Verificar si la clave está correctamente instalada
        'psql -U test_user -d test_db -c "SELECT key_name, length(key_value) as key_length, encode(key_value, \'base64\') as key_base64 FROM encryption_config;"'
    ]

    for cmd in commands:
        result = container.exec_run(cmd)
        logger.info(f"Ejecutando: {cmd}")
        logger.info(f"Resultado:\n{result.output.decode('utf-8')}")


async def _test_encryption(container):
    """Prueba las funciones de encriptación directamente"""
    logger.info("Probando funciones de encriptación...")

    # Crear una tabla de prueba
    setup_commands = [
        'psql -U test_user -d test_db -c "CREATE TEMP TABLE encryption_test (id serial, data text);"',
        'psql -U test_user -d test_db -c "INSERT INTO encryption_test (data) VALUES (\'test_value\');"',
        # Probar encriptación
        'psql -U test_user -d test_db -c "SELECT encrypt_value(data) FROM encryption_test;"',
        # Probar desencriptación
        'psql -U test_user -d test_db -c "SELECT decrypt_value(encrypt_value(data)) FROM encryption_test;"'
    ]

    for cmd in setup_commands:
        result = container.exec_run(cmd)
        logger.info(f"Ejecutando: {cmd}")
        logger.info(f"Resultado:\n{result.output.decode('utf-8')}")

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
