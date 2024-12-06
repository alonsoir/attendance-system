import asyncio
import contextlib
import logging
from pathlib import Path
from typing import AsyncGenerator
from contextlib import asynccontextmanager
import async_timeout
import docker
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

logger = logging.getLogger(__name__)

# Configuración del logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Constantes
CONTAINER_NAME = "test-postgres"
IMAGE = "test-postgres"  # Usar la imagen personalizada
USERNAME = "test_user"
PASSWORD = "test_password"
DBNAME = "test_db"
PORT = 5432

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
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
            s.close()
            return False
        except socket.error:
            return True

def get_free_port() -> int:
    """Encuentra un puerto disponible"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        s.listen(1)
        port = s.getsockname()[1]
        return port


@pytest.fixture(scope="session")
async def postgres_container(event_loop):
    """Proporciona un contenedor PostgreSQL configurado para las pruebas"""
    logger.info("Iniciando fixture del contenedor PostgreSQL")
    container = None
    client = docker.from_env()
    port = get_free_port()
    logger.info(f"Usando puerto {port} para PostgreSQL")

    try:
        # Limpieza de contenedor existente
        try:
            existing = client.containers.get(CONTAINER_NAME)
            logger.info(f"Encontrado contenedor existente {CONTAINER_NAME}. Eliminándolo...")
            existing.stop()
            existing.remove()
            logger.info(f"Contenedor existente {CONTAINER_NAME} eliminado")
        except docker.errors.NotFound:
            logger.info(f"No se encontró contenedor existente {CONTAINER_NAME}")

        # Crear nuevo contenedor
        container = client.containers.run(
            image=IMAGE,
            name=CONTAINER_NAME,
            environment={
                "POSTGRES_USER": USERNAME,
                "POSTGRES_PASSWORD": PASSWORD,
                "POSTGRES_DB": DBNAME
            },
            ports={
                '5432/tcp': ('127.0.0.1', port)
            },
            detach=True,
            remove=True  # Automáticamente elimina el contenedor cuando se detiene
        )

        logger.info(f"Contenedor creado: {container.id}")
        logger.info(f"Estado inicial: {container.status}")

        while container.status != "running":
            logger.info(f"Esperando a que el contenedor esté running... Estado actual: {container.status}")
            await asyncio.sleep(1)
            container.reload()

        logs = container.logs().decode('utf-8')
        logger.info(f"Logs del contenedor:\n{logs}")

        # Esperar a que PostgreSQL esté listo
        logger.info("Esperando a que PostgreSQL esté listo...")
        await _wait_for_postgres(container, port)

        # Inicializar la base de datos
        logger.info("Inicializando la base de datos...")
        await _initialize_database(container, port)
        logger.info("Base de datos inicializada correctamente")

        yield container, port  # Devolvemos también el puerto

    except Exception as e:
        logger.error(f"Error durante la configuración del contenedor: {str(e)}")
        if container:
            logger.info("Limpiando contenedor debido a error...")
            try:
                container.stop()
                container.wait()
                logger.info("Contenedor eliminado después de error")
            except Exception as cleanup_error:
                logger.error(f"Error durante la limpieza del contenedor: {str(cleanup_error)}")
        raise

    finally:
        # Asegurarse de que el contenedor se limpie al final
        if container:
            logger.info(f"Limpieza final del contenedor {container.id}...")
            try:
                container.stop()
                container.wait()  # Esperar a que el contenedor se detenga completamente
                logger.info("Contenedor detenido exitosamente")
            except Exception as e:
                logger.error(f"Error durante la limpieza final del contenedor: {str(e)}")

        # Verificación adicional de limpieza
        try:
            existing = client.containers.get(CONTAINER_NAME)
            logger.warning(
                f"El contenedor {CONTAINER_NAME} sigue existiendo después de la limpieza. Intentando eliminar...")
            existing.stop()
            existing.remove(force=True)
            logger.info("Contenedor eliminado en la verificación final")
        except docker.errors.NotFound:
            logger.info("Verificación final: contenedor eliminado correctamente")

        # Liberar el puerto
        logger.info(f"Liberando puerto {port}")
        with contextlib.suppress(Exception):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('127.0.0.1', port))

async def _wait_for_postgres(container):
    max_attempts = 30
    attempt = 0

    port_bindings = container.attrs['NetworkSettings']['Ports']
    logger.info(f"Configuración de puertos: {port_bindings}")

    async def try_connect():
        conn_str = f"postgresql+asyncpg://{USERNAME}:{PASSWORD}@127.0.0.1:{PORT}/{DBNAME}"
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
            logs = container.logs().decode('utf-8')
            logger.info(f"Últimos logs:\n{logs}")

    raise TimeoutError("PostgreSQL no está disponible después de 30 intentos")


async def _initialize_database(container: docker.models.containers.Container) -> None:
    """Inicializa el esquema y datos de prueba"""
    logger.info("Iniciando inicialización de la base de datos")
    try:
        await _load_schema(container)
        await _load_test_data(container)
        logger.info("Base de datos inicializada correctamente")
    except Exception as e:
        logger.error(f"Error inicializando la base de datos: {str(e)}")
        raise

async def _load_schema(container: docker.models.containers.Container) -> None:
    """Carga el esquema de la base de datos"""
    logger.info("Cargando esquema de la base de datos...")
    schema_path = Path(__file__).resolve().parent.parent / "db" / "schema" / "schema.sql"

    if not schema_path.exists():
        logger.error(f"Archivo de esquema no encontrado en {schema_path}")
        raise FileNotFoundError(f"Archivo de esquema no encontrado en {schema_path}")

    schema_sql = schema_path.read_text()
    logger.debug(f"Contenido del esquema:\n{schema_sql}")

    # Dividir las sentencias SQL en partes más pequeñas
    schema_statements = schema_sql.split(';')

    async with _get_session(container, timeout=480.0) as session:
        logger.info("Ejecutando sentencias SQL del esquema...")
        for statement in schema_statements:
            if statement.strip():
                try:
                    logger.debug(f"Ejecutando sentencia SQL: {statement.strip()}")
                    await session.execute(text(statement.strip()))
                except Exception as e:
                    logger.error(f"Error al ejecutar la sentencia SQL: {statement.strip()}")
                    logger.error(f"Detalles del error: {str(e)}")
                    await session.rollback()  # Rollback solo si hay error
                    raise
        await session.commit()  # Hacer commit si todo salió bien
        logger.info("Esquema de base de datos cargado exitosamente")


async def _load_test_data(container: docker.models.containers.Container) -> None:
    """Carga datos iniciales de prueba"""
    logger.info("Cargando datos de prueba...")
    test_data_path = Path(__file__).parent / "containers/test_data.sql"

    if not test_data_path.exists():
        logger.warning(f"Archivo de datos de prueba no encontrado en {test_data_path}")
        return

    async with _get_session(container) as session:
        async with session.begin():
            # Primero limpiar todas las tablas en el orden correcto
            logger.info("Limpiando tablas existentes...")
            tables = [
                'messages',
                'conversations',
                'tutor_student',
                'students',
                'tutors',
                'schools',
                'service_status'
            ]
            for table in tables:
                logger.info(f"Limpiando tabla {table}...")
                await session.execute(text(f'TRUNCATE TABLE {table} CASCADE'))

            # Ahora cargar los datos de prueba
            test_data_sql = test_data_path.read_text()
            logger.info(f"Contenido de datos de prueba:\n{test_data_sql}")

            # Dividir las sentencias SQL y ejecutarlas una por una
            statements = [stmt for stmt in test_data_sql.split(';') if stmt.strip()]
            for statement in statements:
                try:
                    logger.debug(f"Ejecutando sentencia SQL: {statement.strip()}")
                    await session.execute(text(statement.strip()))
                except Exception as e:
                    logger.error(f"Error al ejecutar la sentencia SQL: {statement.strip()}")
                    logger.error(f"Detalles del error: {str(e)}")
                    raise

            logger.info("Datos de prueba cargados exitosamente")

@pytest.fixture(scope="function")
async def db_session(postgres_container) -> AsyncGenerator[AsyncSession, None]:
    """Proporciona una sesión de base de datos limpia para cada test"""
    container, port = postgres_container
    logger.debug("Creando nueva sesión de base de datos para test")

    async with _get_session(container, port, timeout=480.0) as session:
        yield session
        logger.debug("Limpiando datos después del test")
        await _cleanup_data(container, port)

@contextlib.asynccontextmanager
async def _get_session(container: docker.models.containers.Container, timeout: float = 480.0) -> AsyncGenerator[
    AsyncSession, None]:
    """Proporciona una sesión de base de datos utilizando el contenedor de PostgreSQL"""
    logger.info("Creando sesión de base de datos")

    db_url = _get_db_url(container)
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


async def _cleanup_data(container: docker.models.containers.Container) -> None:
    """Limpia todos los datos de las tablas en el contenedor de PostgreSQL"""
    logger.info("Iniciando limpieza de datos...")

    db_url = _get_db_url(container).replace('postgresql://', 'postgresql+asyncpg://')
    engine = create_async_engine(db_url, echo=True)

    async with engine.begin() as conn:
        tables = [
            'messages',
            'conversations',
            'tutor_student',
            'students',
            'tutors',
            'schools',
            'service_status'  # Asegurarse de limpiar la tabla service_status
        ]
        for table in tables:
            logger.debug(f"Limpiando tabla: {table}")
            await conn.execute(text(f'TRUNCATE TABLE {table} CASCADE;'))

    logger.info("Limpieza de datos completada")