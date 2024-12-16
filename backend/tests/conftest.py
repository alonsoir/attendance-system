import asyncio
import contextlib
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator, Tuple

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
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Constantes
CONTAINER_NAME = "test-postgres"
IMAGE = "test-postgres"  # Usar la imagen personalizada
USERNAME = "test_user"
PASSWORD = "test_password"
DBNAME = "test_db"


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
            existing = client.containers.get(CONTAINER_NAME)
            logger.info(
                f"Encontrado contenedor existente {CONTAINER_NAME}. Eliminándolo..."
            )
            await _remove_container(existing)
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
                "POSTGRES_DB": DBNAME,
            },
            ports={"5432/tcp": ("127.0.0.1", port)},
            detach=True,
            remove=True,
        )

        logger.info(f"Contenedor creado: {container.id}")
        logger.info(f"Estado inicial: {container.status}")

        while container.status != "running":
            logger.info(
                f"Esperando a que el contenedor esté running... Estado actual: {container.status}"
            )
            await asyncio.sleep(1)
            container.reload()

        logs = container.logs().decode("utf-8")
        logger.info(f"Logs del contenedor:\n{logs}")

        # Esperar a que PostgreSQL esté listo
        logger.info("Esperando a que PostgreSQL esté listo...")
        await _wait_for_postgres(container, port)

        # Verificar estado antes de cargar schema
        async with _get_session(container, port) as session:
            try:
                result = await session.execute(text("SELECT COUNT(*) FROM schools"))
                count = result.scalar()
                logger.info(f"Estado inicial antes de schema: {count} escuelas")
            except Exception as e:
                logger.info(f"Estado inicial: tablas no existen aún - {str(e)}")

        # Inicializar schema
        logger.info("=== Iniciando carga de schema... ===")
        await _load_schema(container, port)
        logger.info("=== Schema cargado exitosamente ===")

        # Verificar estado después de cargar schema
        async with _get_session(container, port) as session:
            result = await session.execute(text("SELECT COUNT(*) FROM schools"))
            count = result.scalar()
            logger.info(f"Estado después de schema: {count} escuelas")

        # Cargar datos de prueba
        logger.info("=== Iniciando carga de datos de prueba... ===")
        await _load_test_data(container, port)
        logger.info("=== Datos de prueba cargados ===")

        # Verificar consistencia después de cargar datos
        async with _get_session(container, port) as session:
            logger.info("Verificando consistencia de datos inicial...")
            is_consistent = await _verify_data_consistency(session)
            if not is_consistent:
                logger.error("Datos iniciales inconsistentes")
                raise Exception("Los datos iniciales no son consistentes")

            # Verificar conteo de registros
            result = await session.execute(
                text(
                    """
                SELECT table_name, COUNT(*) 
                FROM (
                    SELECT COUNT(*) as count, 'schools' as table_name FROM schools
                    UNION ALL
                    SELECT COUNT(*), 'students' FROM students
                    UNION ALL
                    SELECT COUNT(*), 'tutors' FROM tutors
                    UNION ALL
                    SELECT COUNT(*), 'tutor_student' FROM tutor_student
                    UNION ALL
                    SELECT COUNT(*), 'conversations' FROM conversations
                    UNION ALL
                    SELECT COUNT(*), 'messages' FROM messages
                    UNION ALL
                    SELECT COUNT(*), 'service_status' FROM service_status
                ) counts
                GROUP BY table_name
            """
                )
            )
            counts = result.fetchall()
            logger.info("Estado después de cargar datos:")
            for table_name, count in counts:
                logger.info(f"  - {table_name}: {count} registros")

        yield container, port

        # Verificar consistencia antes de limpiar
        async with _get_session(container, port) as session:
            logger.info("Verificando consistencia de datos final...")
            is_consistent = await _verify_data_consistency(session)
            if not is_consistent:
                logger.warning("Los datos finales no son consistentes")

    except Exception as e:
        logger.error(f"Error durante la configuración del contenedor: {str(e)}")
        if container:
            logger.info("Limpiando contenedor debido a error...")
            try:
                await _remove_container(container)
                logger.info("Contenedor eliminado después de error")
            except Exception as cleanup_error:
                logger.error(
                    f"Error durante la limpieza del contenedor: {str(cleanup_error)}"
                )
        raise

    finally:
        logger.info("=== Iniciando limpieza final de postgres_container ===")
        if container:
            try:
                logger.info(f"Limpieza final del contenedor {container.id}...")
                await _remove_container(container)
                logger.info("Contenedor detenido y eliminado exitosamente")
            except Exception as e:
                logger.error(
                    f"Error durante la limpieza final del contenedor: {str(e)}"
                )

        # Verificación adicional de limpieza
        try:
            existing = client.containers.get(CONTAINER_NAME)
            logger.warning(
                f"El contenedor {CONTAINER_NAME} sigue existiendo después de la limpieza. Intentando eliminar..."
            )
            await _remove_container(existing)
            logger.info("Contenedor eliminado en la verificación final")
        except docker.errors.NotFound:
            logger.info("Verificación final: contenedor eliminado correctamente")
        except Exception as e:
            logger.error(f"Error durante la verificación final: {str(e)}")

        # Liberar el puerto
        logger.info(f"Liberando puerto {port}")
        with contextlib.suppress(Exception):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(("127.0.0.1", port))

        logger.info("=== FIN postgres_container fixture ===")


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


async def _initialize_database(
    container: docker.models.containers.Container, port: int
) -> None:
    """Inicializa el esquema y datos de prueba"""
    logger.info("Iniciando inicialización de la base de datos")
    try:
        await _load_schema(container, port)
        await _load_test_data(container, port)
        logger.info("Base de datos inicializada correctamente")
    except Exception as e:
        logger.error(f"Error inicializando la base de datos: {str(e)}")
        raise


async def _load_schema(
    container: docker.models.containers.Container, port: int
) -> None:
    """Carga el esquema de la base de datos"""
    logger.info("Cargando esquema de la base de datos...")
    schema_path = (
        Path(__file__).resolve().parent.parent / "db" / "schema" / "schema.sql"
    )

    if not schema_path.exists():
        logger.error(f"Archivo de esquema no encontrado en {schema_path}")
        raise FileNotFoundError(f"Archivo de esquema no encontrado en {schema_path}")

    schema_sql = schema_path.read_text()
    logger.debug(f"Contenido del esquema:\n{schema_sql}")

    # Dividir las sentencias SQL en partes más pequeñas
    schema_statements = schema_sql.split(";")

    async with _get_session(container, port, timeout=480.0) as session:
        logger.info("Ejecutando sentencias SQL del esquema...")
        for statement in schema_statements:
            if statement.strip():
                try:
                    logger.debug(f"Ejecutando sentencia SQL: {statement.strip()}")
                    await session.execute(text(statement.strip()))
                except Exception as e:
                    logger.error(
                        f"Error al ejecutar la sentencia SQL: {statement.strip()}"
                    )
                    logger.error(f"Detalles del error: {str(e)}")
                    await session.rollback()  # Rollback solo si hay error
                    raise
        await session.commit()  # Hacer commit si todo salió bien
        logger.info("Esquema de base de datos cargado exitosamente")


async def _load_test_data(
    container: docker.models.containers.Container, port: int
) -> None:
    """Carga datos iniciales de prueba"""
    logger.info("=== Iniciando carga de datos de prueba ===")

    async with _get_session(container, port) as session:
        try:
            # Primero limpiar todas las tablas en orden
            tables = [
                "messages",
                "conversations",
                "tutor_student",
                "students",
                "tutors",
                "schools",
                "service_status",
            ]

            async with session.begin():
                for table in tables:
                    logger.info(f"Limpiando tabla {table}...")
                    await session.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
                logger.info("Todas las tablas limpiadas")

            # Cargar los datos de prueba
            test_data_path = Path(__file__).parent / "containers/test_data.sql"
            if not test_data_path.exists():
                logger.warning(
                    f"Archivo de datos de prueba no encontrado en {test_data_path}"
                )
                return

            async with session.begin():
                test_data_sql = test_data_path.read_text()
                statements = [
                    stmt.strip() for stmt in test_data_sql.split(";") if stmt.strip()
                ]

                for statement in statements:
                    logger.info(
                        f"Ejecutando: {statement[:100]}..."
                    )  # Log solo los primeros 100 caracteres
                    await session.execute(text(statement))

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


async def verify_data(session):
    """Verifica el estado de todas las tablas principales"""
    counts = {}
    tables = [
        "schools",
        "students",
        "tutors",
        "tutor_student",
        "conversations",
        "messages",
        "service_status",
    ]

    for table in tables:
        result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
        counts[table] = result.scalar()

    logger.info(f"Estado actual de las tablas: {counts}")
    return counts


async def _verify_data_consistency(session):
    """Verifica que los datos estén consistentes entre tablas relacionadas"""
    inconsistencies = []

    try:
        # Verificar relación schools-students
        result = await session.execute(
            text(
                """
            SELECT s.id, s.school_id 
            FROM students s 
            LEFT JOIN schools sch ON s.school_id = sch.id 
            WHERE sch.id IS NULL
        """
            )
        )
        orphan_students = result.fetchall()
        if orphan_students:
            inconsistencies.append(f"Estudiantes sin escuela válida: {orphan_students}")

        # Verificar relación tutor_student
        result = await session.execute(
            text(
                """
            SELECT ts.student_id, ts.tutor_id
            FROM tutor_student ts
            LEFT JOIN students s ON ts.student_id = s.id
            LEFT JOIN tutors t ON ts.tutor_id = t.id
            WHERE s.id IS NULL OR t.id IS NULL
        """
            )
        )
        invalid_relationships = result.fetchall()
        if invalid_relationships:
            inconsistencies.append(
                f"Relaciones tutor-estudiante inválidas: {invalid_relationships}"
            )

        # Verificar relación conversations
        result = await session.execute(
            text(
                """
            SELECT c.id, c.student_id, c.school_id
            FROM conversations c
            LEFT JOIN students s ON c.student_id = s.id
            LEFT JOIN schools sch ON c.school_id = sch.id
            WHERE s.id IS NULL OR sch.id IS NULL
        """
            )
        )
        invalid_conversations = result.fetchall()
        if invalid_conversations:
            inconsistencies.append(
                f"Conversaciones con referencias inválidas: {invalid_conversations}"
            )

        # Verificar relación messages-conversations
        result = await session.execute(
            text(
                """
            SELECT m.id, m.conversation_id
            FROM messages m
            LEFT JOIN conversations c ON m.conversation_id = c.id
            WHERE c.id IS NULL
        """
            )
        )
        orphan_messages = result.fetchall()
        if orphan_messages:
            inconsistencies.append(
                f"Mensajes sin conversación válida: {orphan_messages}"
            )

        if inconsistencies:
            logger.warning("Inconsistencias encontradas:")
            for inconsistency in inconsistencies:
                logger.warning(inconsistency)
            return False

        logger.info(
            "Verificación de consistencia completada: todos los datos son consistentes"
        )
        return True

    except Exception as e:
        logger.error(f"Error durante la verificación de consistencia: {str(e)}")
        return False


@pytest.fixture(scope="function")
async def db_session(postgres_container) -> AsyncGenerator[AsyncSession, None]:
    container, port = postgres_container
    logger.info("=== INICIO db_session fixture ===")
    session = None

    try:
        async with _get_session(container, port, timeout=480.0) as session:
            # Verificar estado inicial
            counts = await verify_data(session)

            if all(count == 0 for count in counts.values()):
                logger.info("Base de datos vacía, reinsertando datos...")
                await session.commit()  # Commit explícito antes de cargar datos
                await _load_test_data(container, port)
                await session.commit()  # Commit explícito después de cargar datos

                # Verificar conteo después de reinsertar
                counts = await verify_data(session)
                logger.info(f"Datos reinsertados, nuevo estado: {counts}")

                # Verificar consistencia de los datos
                is_consistent = await _verify_data_consistency(session)
                if not is_consistent:
                    logger.warning("Los datos reinsertados no son consistentes")

            logger.info("Entregando sesión al test")
            yield session
            logger.info("Test completado, cerrando sesión")

    except Exception as e:
        logger.error(f"Error en db_session: {e}")
        raise
    finally:
        if session:
            try:
                await session.close()
                logger.info("Sesión cerrada exitosamente")
            except Exception as e:
                logger.error(f"Error cerrando sesión: {e}")
        logger.info("=== FIN db_session fixture ===")


@pytest.fixture(scope="function", autouse=True)
async def cleanup_after_test(postgres_container):
    """Limpia la base de datos después de cada test"""
    logger.info("=== INICIO cleanup_after_test ===")
    yield  # Esto ocurre antes del test
    logger.info("=== Ejecutando limpieza post-test ===")

    try:
        container, port = postgres_container
        logger.info("Iniciando limpieza de datos...")
        await _cleanup_data(container, port)
        logger.info("Limpieza completada exitosamente")
    except Exception as e:
        logger.error(f"Error durante la limpieza: {e}")
        raise
    finally:
        logger.info("=== FIN cleanup_after_test ===")


@contextlib.asynccontextmanager
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


async def _cleanup_data(
    container: docker.models.containers.Container, port: int
) -> None:
    """Limpia todos los datos de las tablas en el contenedor de PostgreSQL"""
    logger.info(">>> Iniciando proceso de limpieza de datos")

    db_url = _get_db_url(container, port)
    engine = create_async_engine(
        db_url, echo=False
    )  # Cambiamos echo a False para reducir el ruido

    try:
        async with engine.begin() as conn:
            tables = [
                "messages",
                "conversations",
                "tutor_student",
                "students",
                "tutors",
                "schools",
                "service_status",
            ]
            for table in tables:
                logger.info(f">>> Limpiando tabla: {table}")
                await conn.execute(text(f"TRUNCATE TABLE {table} CASCADE;"))
                logger.info(f">>> Tabla {table} limpiada")
        logger.info(">>> Todas las tablas han sido limpiadas")
    except Exception as e:
        logger.error(f">>> Error en limpieza: {e}")
        raise
    finally:
        await engine.dispose()
        logger.info(">>> Conexión de limpieza cerrada")
