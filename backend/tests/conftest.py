import asyncio
import contextlib
import logging
from pathlib import Path
from typing import AsyncGenerator
import socket
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
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Constantes
CONTAINER_NAME = "attendance_system-coordinator-1"
IMAGE = "test-postgres-full-citus"  # Usar la imagen personalizada
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
    logger.info("=== INICIO postgres_container fixture ===")
    container = None
    client = docker.from_env()
    port = get_free_port()
    logger.info(f"Puerto asignado para PostgreSQL: {port}")

    try:
        # Limpieza de contenedor existente
        try:
            logger.info(client.containers.list())
            existing = client.containers.get(CONTAINER_NAME)
            logger.info(f"Encontrado contenedor existente {CONTAINER_NAME}. {existing}")
            container=existing
            # logger.info(f"Encontrado contenedor existente {CONTAINER_NAME}. Eliminándolo...")
            # await _remove_container(existing)
            # logger.info(f"Contenedor existente {CONTAINER_NAME} eliminado")
        except docker.errors.NotFound:
            logger.info(f"No se encontró contenedor existente {CONTAINER_NAME}")
        '''
        # Crear nuevo contenedor con más opciones de configuración
        container_config = {
            "image": IMAGE,
            "name": CONTAINER_NAME,
            "environment": {
                "POSTGRES_USER": USERNAME,
                "POSTGRES_PASSWORD": PASSWORD,
                "POSTGRES_DB": DBNAME,
                "POSTGRES_HOST": "0.0.0.0",
                "POSTGRES_LISTEN_ADDRESSES": "*",
                "POSTGRES_HOST_AUTH_METHOD": "md5",
                "PGDATA": "/var/lib/postgresql/data/pgdata",
                # Configurar todas las extensiones requeridas
                "POSTGRES_SHARED_PRELOAD_LIBRARIES": "pg_cron,citus",
                "POSTGRES_CRON_DATABASE": DBNAME,
                "CITUS_EXTENSION_VERSION": "12.1"  # Ajusta la versión según tu imagen
            },
            "ports": {"5432/tcp": ("127.0.0.1", port)},
            "detach": True,
            "remove": False,
            "network_mode": "bridge",
            "healthcheck": {
                "test": ["CMD-SHELL", f"pg_isready -U {USERNAME} -d {DBNAME}"],
                "interval": 1000000000,
                "timeout": 1000000000,
                "retries": 5,
                "start_period": 2000000000
            },
            "command": [
                "postgres",
                "-c", "listen_addresses=*",
                "-c", "max_connections=100",
                "-c", "shared_preload_libraries=pg_cron,citus",
                "-c", f"cron.database_name={DBNAME}",
                "-c", "cron.use_background_workers=on",
                "-c", "max_prepared_transactions=150"  # Requerido para Citus
            ],
            "volumes": {
                "/tmp/pgdata": {"bind": "/var/lib/postgresql/data", "mode": "rw"}
            }
        }

        logger.info("Creando contenedor con la siguiente configuración:")
        logger.info(str(container_config))

        container = client.containers.run(**container_config)
        logger.info(f"Contenedor creado: {container.id}")
        '''
        # Esperar a que el contenedor esté en estado running
        max_wait = 30
        wait_count = 0
        while wait_count < max_wait:
            # container.reload()
            current_status = container.status
            logger.info(f"Estado actual del contenedor: {current_status}")

            if current_status == "running":
                logger.info("Contenedor en estado running")
                break

            if current_status in ["exited", "dead"]:
                logs = container.logs().decode('utf-8')
                logger.error(f"Contenedor terminado inesperadamente. Logs:\n{logs}")
                raise Exception("El contenedor terminó inesperadamente")

            wait_count += 1
            await asyncio.sleep(1)

        if wait_count >= max_wait:
            raise TimeoutError("Tiempo de espera agotado esperando que el contenedor esté running")

        # Esperar a que PostgreSQL esté listo
        # await _wait_for_postgres(container, port)

        yield container, port

    except Exception as e:
        logger.error(f"Error durante la configuración del contenedor: {str(e)}")
        if container:
            logger.info("Limpiando contenedor debido a error...")
            try:
                container.stop(timeout=5)
                container.remove(force=True)
                logger.info("Contenedor eliminado después de error")
            except Exception as cleanup_error:
                logger.error(f"Error durante la limpieza del contenedor: {str(cleanup_error)}")
        raise
    '''
    finally:
        logger.info("=== Iniciando limpieza final ===")
        if container:
            try:
                logger.info(f"Deteniendo contenedor {container.id}...")
                container.stop(timeout=5)
                logger.info(f"Eliminando contenedor {container.id}...")
                container.remove(force=True)
                logger.info("Contenedor eliminado exitosamente")
            except Exception as e:
                logger.error(f"Error durante la limpieza final: {str(e)}")
    '''

async def _verify_extensions(container):
    logger.info("Verificando instalación de extensiones...")
    required_extensions = ['pg_cron', 'pgcrypto', 'uuid-ossp', 'citus']

    try:
        for ext in required_extensions:
            result = container.exec_run(
                [
                    "psql",
                    "-U", USERNAME,
                    "-d", DBNAME,
                    "-c", f"CREATE EXTENSION IF NOT EXISTS {ext};"
                ],
                environment={"PGPASSWORD": PASSWORD}
            )

            output = result.output.decode()
            if result.exit_code != 0:
                logger.error(f"Error al crear extensión {ext}: {output}")
                raise Exception(f"Error al crear extensión {ext}: {output}")

            # Verificar que la extensión está instalada
            verify_result = container.exec_run(
                [
                    "psql",
                    "-U", USERNAME,
                    "-d", DBNAME,
                    "-c", f"SELECT extname, extversion FROM pg_extension WHERE extname = '{ext}';"
                ],
                environment={"PGPASSWORD": PASSWORD}
            )

            verify_output = verify_result.output.decode()
            if ext not in verify_output:
                logger.error(f"La extensión {ext} no se instaló correctamente")
                raise Exception(f"La extensión {ext} no se instaló correctamente")

            logger.info(f"Extensión {ext} instalada correctamente")

        return True

    except Exception as e:
        logger.error(f"Error al verificar extensiones: {e}")
        raise

async def _verify_psql_connection(container, port):
    logger.info("Verificando conexión mediante psql...")
    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            result = container.exec_run(
                [
                    "psql",
                    "-h", "localhost",
                    "-p", "5432",
                    "-U", USERNAME,
                    "-d", DBNAME,
                    "-c", "SELECT 1"
                ],
                environment={
                    "PGPASSWORD": PASSWORD,
                    "LANG": "en_US.utf8"
                }
            )

            output = result.output.decode()
            logger.info(f"Resultado verificación psql (intento {retry_count + 1}): {output}")

            if result.exit_code == 0 and "1 row" in output:
                logger.info("Verificación psql exitosa")
                return True

            logger.warning(f"Verificación psql fallida (intento {retry_count + 1})")
            retry_count += 1
            await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Error en verificación psql (intento {retry_count + 1}): {e}")
            retry_count += 1
            await asyncio.sleep(1)

    return False


async def _wait_for_postgres(container, port):
    max_attempts = 30
    attempt = 0

    # Espera inicial más larga
    logger.info("Esperando 10 segundos iniciales para estabilización...")
    await asyncio.sleep(10)

    port_bindings = container.attrs["NetworkSettings"]["Ports"]
    logger.info(f"Configuración de puertos: {port_bindings}")

    while attempt < max_attempts:
        try:
            # Verificar conexión básica
            if await _verify_psql_connection(container, port):
                logger.info("Verificación psql exitosa")

                # Verificar instalación de extensiones
                if await _verify_extensions(container):
                    logger.info("Todas las extensiones verificadas correctamente")
                    return

            else:
                logger.warning("Verificación psql fallida")

        except Exception as e:
            logger.error(f"Intento {attempt + 1} fallido: {str(e)}")

            # Verificación detallada del estado
            container.reload()
            state = container.attrs.get('State', {})
            health = state.get('Health', {})

            logger.info(f"Estado del contenedor: {container.status}")
            logger.info(f"Estado de salud: {health.get('Status', 'N/A')}")
            logger.info(f"Último chequeo: {health.get('Log', [{}])[-1].get('Output', 'N/A')}")

            # Obtener logs recientes
            recent_logs = container.logs(tail=50, timestamps=True).decode("utf-8")
            logger.info(f"Logs recientes:\n{recent_logs}")

            attempt += 1
            if attempt < max_attempts:
                await asyncio.sleep(5)

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
            logger.info(f"Intento {attempt + 1} de eliminar contenedor {container.id}")

            # Intentar detener el contenedor primero
            try:
                container.stop(timeout=10)
                logger.info("Contenedor detenido correctamente")
            except Exception as stop_error:
                logger.warning(f"Error al detener contenedor: {stop_error}")

            # Esperar un momento antes de intentar eliminar
            await asyncio.sleep(2)

            # Intentar eliminar el contenedor
            container.remove(force=True)
            logger.info("Contenedor eliminado correctamente")
            return True

        except Exception as e:
            if attempt == retries - 1:
                logger.error(f"No se pudo eliminar el contenedor después de {retries} intentos: {e}")
                return False
            logger.warning(f"Intento {attempt + 1} fallido al eliminar contenedor: {e}")
            await asyncio.sleep(2)


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
            '''
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
            '''
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
        # await _cleanup_data(container, port)
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
    """Obtiene la URL de conexión a la base de datos con parámetros adicionales"""
    params = {
        "application_name": "test_connection",
        "connect_timeout": "10",
        "client_encoding": "utf8"
    }
    param_string = "&".join(f"{k}={v}" for k, v in params.items())
    return f"postgresql+asyncpg://{USERNAME}:{PASSWORD}@127.0.0.1:{port}/{DBNAME}?{param_string}"


async def _diagnose_connection(container, port):
    """Función de diagnóstico para problemas de conexión"""
    logger.info("=== Iniciando diagnóstico de conexión ===")

    # Verificar red
    networks = container.attrs.get('NetworkSettings', {}).get('Networks', {})
    logger.info(f"Configuración de red: {networks}")

    # Verificar puertos
    ports = container.attrs.get('NetworkSettings', {}).get('Ports', {})
    logger.info(f"Mapeo de puertos: {ports}")

    # Verificar estado del contenedor
    state = container.attrs.get('State', {})
    logger.info(f"Estado detallado: {state}")

    # Intentar netcat
    try:
        result = container.exec_run(f"nc -zv 127.0.0.1 {port}")
        logger.info(f"Prueba netcat: {result.output.decode()}")
    except Exception as e:
        logger.error(f"Error en prueba netcat: {e}")

    logger.info("=== Fin diagnóstico de conexión ===")

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
