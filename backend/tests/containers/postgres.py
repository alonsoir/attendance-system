import logging
import time
from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer

from ..utils.docker_check import check_docker

logger = logging.getLogger(__name__)


class PostgresTestContainer:
    POSTGRES_USERNAME = "test"
    POSTGRES_PASSWORD = "test"
    POSTGRES_DB = "test"
    POSTGRES_PORT = 5432

    def __init__(self):
        logger.info("Inicializando PostgresTestContainer")
        if not check_docker():
            logger.error("Docker no está disponible o no está corriendo")
            raise RuntimeError("Docker no está disponible o no está corriendo")


        self.container = PostgresContainer(
            image="postgres:15",
            username=self.POSTGRES_USERNAME,
            password=self.POSTGRES_PASSWORD,
            dbname=self.POSTGRES_DB,
            port=self.POSTGRES_PORT,
        )
        self.engine = None
        self.session_factory = None
        logger.info("PostgresTestContainer inicializado")

    async def start(self) -> None:
        """Inicia el contenedor y configura la base de datos"""
        start_time = time.time()
        logger.info("Iniciando contenedor PostgreSQL...")

        try:
            self.container.start()
            logger.info(
                f"Contenedor iniciado:\n"
                f"- Host: {self.container.get_container_host_ip()}\n"
                f"- Puerto: {self.container.get_exposed_port(self.POSTGRES_PORT)}\n"
                f"- URL conexión: {self.container.get_connection_url()}"
            )
        except Exception as e:
            logger.error(f"Error al iniciar el contenedor: {str(e)}")
            raise

        # Crear engine asíncrono
        db_url = self.container.get_connection_url()
        async_url = db_url.replace('postgresql://', 'postgresql+asyncpg://')
        logger.info(f"URL de conexión AsyncPG: {async_url}")

        self.engine = create_async_engine(
            async_url,
            echo=True
        )

        # Crear session factory
        self.session_factory = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        logger.info("Session factory creado")

        # Inicializar base de datos
        await self._initialize_database()

        end_time = time.time()
        logger.info(f"Contenedor PostgreSQL iniciado y configurado en {end_time - start_time:.2f} segundos")

    async def _initialize_database(self) -> None:
        """Inicializa el esquema y datos de prueba"""
        logger.info("Iniciando inicialización de la base de datos")
        try:
            # Cargar el esquema
            await self._load_schema()
            # Cargar datos iniciales
            await self._load_test_data()
            logger.info("Base de datos inicializada correctamente")
        except Exception as e:
            logger.error(f"Error inicializando la base de datos: {str(e)}")
            raise

    async def _load_schema(self) -> None:
        """Carga el esquema de la base de datos"""
        logger.info("Cargando esquema de la base de datos...")
        schema_path = Path(__file__).parent.parent.parent / "db" / "schema" / "schema.sql"

        if not schema_path.exists():
            logger.error(f"Archivo de esquema no encontrado en {schema_path}")
            raise FileNotFoundError(f"Archivo de esquema no encontrado en {schema_path}")

        schema_sql = schema_path.read_text()
        logger.debug(f"Contenido del esquema:\n{schema_sql}")

        async with self.engine.begin() as conn:
            logger.info("Ejecutando sentencias SQL del esquema...")
            await conn.execute(schema_sql)
            logger.info("Esquema de base de datos cargado exitosamente")

    async def _load_test_data(self) -> None:
        """Carga datos iniciales de prueba"""
        logger.info("Cargando datos de prueba...")
        test_data_path = Path(__file__).parent / "test_data.sql"

        if not test_data_path.exists():
            logger.warning(f"Archivo de datos de prueba no encontrado en {test_data_path}")
            return

        test_data_sql = test_data_path.read_text()
        logger.debug(f"Contenido de datos de prueba:\n{test_data_sql}")

        async with self.engine.begin() as conn:
            logger.info("Ejecutando sentencias SQL de datos de prueba...")
            await conn.execute(test_data_sql)
            logger.info("Datos de prueba cargados exitosamente")

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Proporciona una sesión de base de datos"""
        if not self.session_factory:
            logger.error("Intento de obtener sesión sin inicializar el contenedor")
            raise RuntimeError("Container no iniciado. Llama a start() primero")

        logger.debug("Creando nueva sesión de base de datos")
        async with self.session_factory() as session:
            try:
                yield session
                logger.debug("Sesión proporcionada correctamente")
            finally:
                logger.debug("Ejecutando rollback en la sesión")
                await session.rollback()

    async def cleanup_data(self) -> None:
        """Limpia todos los datos de las tablas"""
        logger.info("Iniciando limpieza de datos...")
        tables = [
            'messages',
            'conversations',
            'tutor_student',
            'students',
            'tutors',
            'schools'
        ]

        async with self.engine.begin() as conn:
            for table in tables:
                logger.debug(f"Limpiando tabla: {table}")
                await conn.execute(f'TRUNCATE TABLE {table} CASCADE;')
        logger.info("Limpieza de datos completada")

    async def stop(self) -> None:
        """Detiene el contenedor y limpia recursos"""
        logger.info("Iniciando parada del contenedor...")
        if self.engine:
            logger.debug("Cerrando conexiones de base de datos...")
            await self.engine.dispose()

        logger.debug("Deteniendo contenedor Docker...")
        self.container.stop()
        logger.info("Contenedor PostgreSQL detenido correctamente")