import logging
from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer

logger = logging.getLogger(__name__)


class PostgresTestContainer:
    def __init__(self):
        self.container = PostgresContainer("postgres:15")
        self.engine = None
        self.session_factory = None

    async def start(self) -> None:
        """Inicia el contenedor y configura la base de datos"""
        self.container.start()

        # Crear engine asíncrono
        self.engine = create_async_engine(
            self.container.get_connection_url().replace('postgresql://', 'postgresql+asyncpg://'),
            echo=True
        )

        # Crear session factory
        self.session_factory = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

        # Cargar esquema
        await self._load_schema()

    async def _load_schema(self) -> None:
        """Carga el esquema SQL desde el archivo"""
        schema_path = Path(__file__).parent.parent.parent / "db" / "schema" / "schema.sql"

        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found at {schema_path}")

        # Leer el archivo SQL
        with open(schema_path) as f:
            schema_sql = f.read()

        # Ejecutar el schema
        async with self.engine.begin() as conn:
            await conn.execute(schema_sql)

    async def stop(self) -> None:
        """Detiene el contenedor y limpia recursos"""
        if self.engine:
            await self.engine.dispose()
        self.container.stop()

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Proporciona una sesión de base de datos"""
        async with self.session_factory() as session:
            yield session

    def get_connection_string(self) -> str:
        """Devuelve la URL de conexión"""
        return self.container.get_connection_url()