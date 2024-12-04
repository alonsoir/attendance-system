"""
Base de datos para la aplicación.
"""
import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool

from backend.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class Base:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

Base = declarative_base(cls=Base)

class DatabaseManager:
    _instance: Optional['DatabaseManager'] = None
    _engine: Optional[AsyncEngine] = None
    _sessionmaker: Optional[sessionmaker] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls) -> 'DatabaseManager':
        if cls._instance is None:
            cls._instance = DatabaseManager()
        return cls._instance

    def init_engine(self) -> AsyncEngine:
        """Inicializa el engine de base de datos."""
        if not self._engine:
            logger.info("Inicializando engine de base de datos...")
            try:
                self._engine = create_async_engine(
                    settings.DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://'),
                    echo=settings.DB_ECHO_LOG,
                    poolclass=NullPool
                )
                logger.info("Engine de base de datos inicializado correctamente")
            except Exception as e:
                logger.error(f"Error inicializando engine: {str(e)}")
                raise

        return self._engine

    def get_sessionmaker(self) -> sessionmaker:
        """Obtiene el sessionmaker para crear sesiones de base de datos."""
        if not self._sessionmaker:
            if not self._engine:
                self.init_engine()

            self._sessionmaker = sessionmaker(
                self._engine,
                class_=AsyncSession,
                expire_on_commit=False
            )

        return self._sessionmaker

    async def initialize_db(self) -> None:
        """
        Inicializa la base de datos y crea todas las tablas necesarias.
        """
        from .models import (
            School,
            Tutor,
            Student,
            TutorStudent,
            Conversation,
            Message
        )

        logger.info("Iniciando inicialización de base de datos...")

        try:
            engine = self.init_engine()
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                logger.info("Tablas creadas correctamente")

            # Insertar datos iniciales si es necesario
            await self._init_default_data()

            logger.info("Base de datos inicializada correctamente")

        except Exception as e:
            logger.error(f"Error inicializando base de datos: {str(e)}")
            raise

    async def _init_default_data(self) -> None:
        """
        Inicializa datos por defecto en la base de datos si es necesario.
        """
        async with self.get_sessionmaker()() as session:
            try:
                # Aquí puedes añadir la inserción de datos por defecto
                # Por ejemplo, escuelas predeterminadas, etc.
                await session.commit()
                logger.info("Datos iniciales insertados correctamente")
            except Exception as e:
                await session.rollback()
                logger.error(f"Error insertando datos iniciales: {str(e)}")
                raise

    async def cleanup(self) -> None:
        """Limpia recursos de base de datos."""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._sessionmaker = None
            logger.info("Recursos de base de datos liberados")

# Instancia global para usar en la aplicación
db = DatabaseManager.get_instance()