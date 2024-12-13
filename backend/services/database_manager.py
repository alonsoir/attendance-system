import asyncio
import logging
import threading
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Callable, Optional

import asyncpg
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.core.config import get_settings
from backend.db.models_acl import User, AuditLog

logger = logging.getLogger(__name__)

Base = declarative_base()

class DatabaseManager:
    """
    Singleton que gestiona la conexión a la base de datos PostgreSQL.
    """
    _instance: Optional['DatabaseManager'] = None
    _lock = threading.Lock()

    def __init__(self, settings=None, encrypt_key=None):
        self.settings = settings or get_settings()
        self.encrypt_key = encrypt_key
        self.pool: asyncpg.Pool = None
        self.max_connections: int = 0
        self.engine = create_engine(
            f"postgresql+asyncpg://{self.settings.POSTGRES_USER}:{self.settings.POSTGRES_PASSWORD}"
            f"@{self.settings.POSTGRES_SERVER}:{self.settings.POSTGRES_PORT}/{self.settings.POSTGRES_DB}",
            echo=True  # Para pruebas, podríamos parametrizar esto también
        )
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)

    @classmethod
    def get_instance(cls, settings=None, encrypt_key=None) -> 'DatabaseManager':
        """
        Obtiene la instancia única del DatabaseManager.
        Permite inyección de configuración para pruebas.
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls(settings=settings, encrypt_key=encrypt_key)
            return cls._instance

    @classmethod
    def reset_instance(cls):
        """
        Resetea la instancia del singleton.
        Útil para pruebas.
        """
        with cls._lock:
            cls._instance = None

    async def connect(self, encrypt_key=None) -> None:
        """
        Crea un pool de conexiones a la base de datos.
        """
        try:
            logger.info("Conectando a la base de datos...")
            self.pool = await asyncpg.create_pool(
                user=self.settings.POSTGRES_USER,
                password=self.settings.POSTGRES_PASSWORD,
                host=self.settings.POSTGRES_SERVER,
                port=self.settings.POSTGRES_PORT,
                database=self.settings.POSTGRES_DB,
                min_size=2,
                max_size=10
            )

            # Verificar que la encriptación está inicializada
            async with self.pool.acquire() as conn:
                result = await conn.fetchval(
                    "SELECT key_value FROM encryption_config WHERE key_name = 'main_key'"
                )
                if result:
                    logger.info("Sistema de encriptación ya inicializado")
                else:
                    logger.info("Inicializando sistema de encriptación...")
                    await conn.execute("SELECT generate_encryption_key()")

            logger.info("Conexión a la base de datos establecida correctamente")
        except Exception as e:
            logger.error(f"Error al conectar a la base de datos: {e}")
            raise

    async def disconnect(self) -> None:
        """
        Cierra el pool de conexiones a la base de datos.
        """
        try:
            if self.pool:
                logger.info("Cerrando conexión a la base de datos...")
                await self.pool.close()
                logger.info("Conexión a la base de datos cerrada correctamente")
        except Exception as e:
            logger.error(f"Error al cerrar la conexión a la base de datos: {e}")
            raise

    @contextmanager
    async def transaction(self, user: User = None) -> Callable[..., Any]:
        """
        Proporciona un contexto de transacción para ejecutar consultas.
        User es opcional para permitir pruebas sin usuario.
        """
        async with self.pool.acquire() as conn:
            try:
                async with conn.transaction():
                    yield conn
                    if user:
                        await self._log_audit_event(user, "TRANSACTION_COMMITTED", "DATABASE")
            except Exception as e:
                logger.error(f"Error durante la transacción: {e}")
                if user:
                    await self._log_audit_event(user, "TRANSACTION_ROLLBACK", "DATABASE")
                raise

    async def execute_procedure(self, user: User, procedure_name: str, *args: Any) -> None:
        """
        Ejecuta un procedimiento almacenado en la base de datos.
        """
        try:
            logger.info(f"Ejecutando procedimiento '{procedure_name}'...")
            async with self.transaction(user) as conn:
                await conn.execute(f"CALL {procedure_name}({','.join(['$1'] * len(args))})", *args)
            logger.info(f"Procedimiento '{procedure_name}' ejecutado correctamente")
            await self._log_audit_event(user, f"EXECUTED_PROCEDURE:{procedure_name}", "DATABASE")
        except (asyncpg.PostgresError, Exception) as e:
            logger.error(f"Error al ejecutar el procedimiento '{procedure_name}': {e}")
            await self._log_audit_event(user, f"FAILED_PROCEDURE:{procedure_name}", "DATABASE")
            raise

    async def get_schools(self, user: User) -> list[dict]:
        """
        Obtiene todas las escuelas con sus campos desencriptados.
        """
        try:
            logger.info("Obteniendo escuelas...")
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT 
                        id,
                        decrypt_value(name) as name,
                        decrypt_value(phone) as phone,
                        decrypt_value(address) as address,
                        decrypt_value(country) as country
                    FROM schools
                """)

                schools = [dict(row) for row in rows]
                await self._log_audit_event(user, "GET_SCHOOLS", "DATABASE")
                return schools

        except Exception as e:
            logger.error(f"Error al obtener escuelas: {e}")
            await self._log_audit_event(user, "FAILED_GET_SCHOOLS", "DATABASE")
            raise

    async def _get_max_connections(self) -> int:
        """
        Obtiene la capacidad máxima de conexiones del contenedor PostgreSQL.
        """
        try:
            logger.info("Obteniendo capacidad máxima de conexiones del contenedor PostgreSQL...")
            async with self.pool.acquire() as conn:
                result = await conn.fetch("SHOW max_connections;")
                max_connections = int(result[0]["max_connections"])
                logger.info(f"Capacidad máxima de conexiones: {max_connections}")
                return max_connections
        except (asyncpg.PostgresError, Exception) as e:
            logger.error(f"Error al obtener la capacidad máxima de conexiones: {e}")
            raise

    async def _log_audit_event(self, user: User, action: str, resource: str) -> None:
        """
        Registra un evento de auditoría en la base de datos.
        """
        try:
            async with self.session_factory() as session:
                audit_log = AuditLog(
                    user_id=user.id,
                    action=action,
                    resource=resource,
                    timestamp=datetime.now()
                )
                session.add(audit_log)
                await session.commit()
        except Exception as e:
            logger.error(f"Error al registrar el evento de auditoría: {e}")

    async def monitor_database(self) -> None:
        """
        Monitorea el estado de la base de datos y registra métricas.
        """
        try:
            while True:
                logger.info("Monitoreando estado de la base de datos...")
                await self._check_database_health()
                await asyncio.sleep(60)  # Monitorear cada minuto
        except Exception as e:
            logger.error(f"Error durante el monitoreo de la base de datos: {e}")

    async def _check_database_health(self) -> None:
        """
        Verifica el estado de salud de la base de datos y registra métricas.
        """
        try:
            async with self.pool.acquire() as conn:
                # Verificar conexiones activas
                result = await conn.fetch("SELECT COUNT(*) AS active_connections FROM pg_stat_activity;")
                active_connections = result[0]["active_connections"]
                logger.info(f"Conexiones activas: {active_connections}")

                # Verificar latencia de consultas
                result = await conn.fetch("SELECT now() - pg_backend_timestamp() AS query_latency;")
                query_latency = result[0]["query_latency"].total_seconds()
                logger.info(f"Latencia de consultas: {query_latency} segundos")

                # Verificar espacio en disco
                result = await conn.fetch("SELECT pg_database_size(current_database()) AS database_size;")
                database_size = result[0]["database_size"]
                logger.info(f"Tamaño de la base de datos: {database_size / (1024 ** 3):.2f} GB")

                # Registrar métricas en un sistema de monitorización (p.ej. Prometheus)
                self._record_database_metrics(active_connections, query_latency, database_size)
        except Exception as e:
            logger.error(f"Error al verificar el estado de salud de la base de datos: {e}")

    def _record_database_metrics(self, active_connections: int, query_latency: float, database_size: int) -> None:
        """
        Registra métricas de la base de datos en un sistema de monitorización.
        """
        # Aquí irá el código para enviar las métricas a un sistema como Prometheus
        pass

    async def scale_database(self) -> None:
        """
        Escala horizontalmente la base de datos utilizando sharding.
        """
        try:
            logger.info("Escalando base de datos horizontalmente...")
            # Implementación del sharding de datos
            pass
        except Exception as e:
            logger.error(f"Error al escalar la base de datos: {e}")

    async def enable_high_availability(self) -> None:
        """
        Habilita alta disponibilidad para la base de datos utilizando réplicas.
        """
        try:
            logger.info("Habilitando alta disponibilidad para la base de datos...")
            # Implementación de la alta disponibilidad con réplicas
            pass
        except Exception as e:
            logger.error(f"Error al habilitar la alta disponibilidad: {e}")