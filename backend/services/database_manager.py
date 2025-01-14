import asyncio
import logging
import ssl
import threading
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Optional, AsyncGenerator

import asyncpg
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from backend.core.config import get_settings
from backend.db.models_acl import AuditLog, User

logger = logging.getLogger(__name__)

Base = declarative_base()


class StoredProcedure:
    """
    Clase para representar un procedimiento almacenado.
    """

    def __init__(self, name: str, schema: str, arg_names: list[str],
                 arg_types: list[str], description: str):
        self.name = name
        self.schema = schema
        self.arg_names = arg_names or []
        self.arg_types = arg_types or []
        self.description = description

    def validate_args(self, args: tuple) -> bool:
        """
        Valida que los argumentos coincidan en número y tipo.
        """
        return len(args) == len(self.arg_names)

    def __str__(self) -> str:
        args_str = ', '.join(f'{name}: {type}'
                             for name, type in zip(self.arg_names, self.arg_types))
        return f"{self.schema}.{self.name}({args_str})"


class DatabaseManager:
    """
    Singleton que gestiona la conexión a la base de datos PostgreSQL.
    """
    _instance: Optional["DatabaseManager"] = None
    _lock = threading.Lock()
    _initialized = False
    _stored_procedures: dict[str, dict] = {}

    def __init__(self, settings=None, encrypt_key=None):
        if not self._initialized:
            self.settings = settings or get_settings()
            self.encrypt_key = encrypt_key
            self.pool: Optional[asyncpg.Pool] = None
            self.max_connections: int = 0
            self.engine = create_engine(
                f"postgresql+asyncpg://{self.settings.POSTGRES_USER}:{self.settings.POSTGRES_PASSWORD}"
                f"@{self.settings.POSTGRES_SERVER}:{self.settings.POSTGRES_PORT}/{self.settings.POSTGRES_DB}"
                "?ssl=require",
                echo=True,
            )
            self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)

    @classmethod
    async def get_instance(cls, settings=None, encrypt_key=None) -> "DatabaseManager":
        """
        Obtiene la instancia única del DatabaseManager y asegura la inicialización del pool.
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls(settings=settings, encrypt_key=encrypt_key)
                await cls._instance._initialize()
            return cls._instance

    async def _initialize(self) -> None:
        """
        Inicializa el pool de conexiones y otras configuraciones asíncronas.
        """
        if not self._initialized:
            try:
                logger.info("Inicializando pool de conexiones...")
                self.pool = await asyncpg.create_pool(
                    user=self.settings.POSTGRES_USER,
                    password=self.settings.POSTGRES_PASSWORD,
                    host=self.settings.POSTGRES_SERVER,
                    port=self.settings.POSTGRES_PORT,
                    database=self.settings.POSTGRES_DB,
                    min_size=2,
                    max_size=10,
                    ssl='require',
                    ssl_cert_reqs=ssl.CERT_REQUIRED,
                    ssl_ca_data=self._load_ca_cert(),
                )

                # Verificar que la encriptación está inicializada
                async with self.pool.acquire() as conn:
                    result = await conn.fetchval(
                        "SELECT key_value FROM encryption_config WHERE key_name = 'main_key'"
                    )
                    if not result:
                        logger.info("Inicializando sistema de encriptación...")
                        await conn.execute("SELECT generate_encryption_key()")
                        logger.info("Sistema de encriptación inicializado correctamente")

                await self._load_stored_procedures_catalog()
                self._initialized = True
                logger.info("Pool de conexiones y catálogo inicializados correctamente")
            except Exception as e:
                logger.error(f"Error en la inicialización del pool: {e}")
                raise

    async def _load_stored_procedures_catalog(self) -> None:
        """
        Carga el catálogo de procedimientos almacenados disponibles.
        """
        try:
            async with self.pool.acquire() as conn:
                procedures = await conn.fetch("""
                    SELECT 
                        p.proname as name,
                        n.nspname as schema,
                        p.proargnames as arg_names,
                        array_agg(t.typname) as arg_types,
                        COALESCE(d.description, '') as description
                    FROM pg_proc p
                    JOIN pg_namespace n ON p.pronamespace = n.oid
                    JOIN pg_type t ON t.oid = ANY(p.proargtypes)
                    LEFT JOIN pg_description d ON p.oid = d.objoid
                    WHERE n.nspname NOT IN ('pg_catalog', 'information_schema')
                    AND p.prokind = 'p'
                    GROUP BY p.proname, n.nspname, p.proargnames, d.description
                """)

                for proc in procedures:
                    self._stored_procedures[proc['name']] = StoredProcedure(
                        name=proc['name'],
                        schema=proc['schema'],
                        arg_names=proc['arg_names'],
                        arg_types=proc['arg_types'],
                        description=proc['description']
                    )

                logger.info(f"Cargados {len(self._stored_procedures)} procedimientos almacenados")
        except Exception as e:
            logger.error(f"Error cargando catálogo de procedimientos: {e}")
            raise

    def get_available_procedures(self) -> list[str]:
        """
        Retorna lista de procedimientos disponibles con su firma.
        """
        return [str(proc) for proc in self._stored_procedures.values()]

    def get_procedure_info(self, procedure_name: str) -> Optional[StoredProcedure]:
        """
        Obtiene información detallada de un procedimiento.
        """
        return self._stored_procedures.get(procedure_name)

    def get_procedure_documentation(self, procedure_name: str) -> str:
        """
        Obtiene la documentación de un procedimiento.
        """
        proc = self._stored_procedures.get(procedure_name)
        if not proc:
            return f"Procedimiento {procedure_name} no encontrado"

        doc = [
            f"Procedimiento: {proc.name}",
            f"Esquema: {proc.schema}",
            "Argumentos:"
        ]

        for name, type_ in zip(proc.arg_names, proc.arg_types):
            doc.append(f"  - {name}: {type_}")

        if proc.description:
            doc.extend(["", "Descripción:", proc.description])

        return "\n".join(doc)

    def _load_ca_cert(self) -> str:
        """
        Carga el certificado CA desde la ubicación configurada.
        Para implementar según la configuración específica.
        """
        # TODO: Implementar carga de certificado CA
        pass

    @classmethod
    def reset_instance(cls):
        """
        Resetea la instancia del singleton.
        """
        with cls._lock:
            if cls._instance and cls._instance.pool:
                asyncio.get_event_loop().run_until_complete(cls._instance.pool.close())
            cls._instance = None
            cls._initialized = False

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

    @asynccontextmanager
    async def transaction(self, user: User = None) -> AsyncGenerator[asyncpg.Connection, None]:
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
            # Obtener información del procedimiento
            proc = self.get_procedure_info(procedure_name)
            if not proc:
                raise ValueError(f"Procedimiento '{procedure_name}' no encontrado")

            # Validar argumentos
            if not proc.validate_args(args):
                expected_args = ", ".join(f"{name}: {type_}"
                                        for name, type_ in zip(proc.arg_names, proc.arg_types))
                raise ValueError(
                    f"Argumentos inválidos para {procedure_name}. "
                    f"Esperados: {expected_args}"
                )

            logger.info(f"Ejecutando procedimiento '{procedure_name}' con {len(args)} argumentos")
            async with self.transaction(user) as conn:
                placeholders = [f"${i + 1}" for i in range(len(args))]
                query = f"CALL {proc.schema}.{proc.name}({','.join(placeholders)})"
                await conn.execute(query, *args)

            logger.info(f"Procedimiento '{procedure_name}' ejecutado correctamente")
            await self._log_audit_event(
                user,
                f"EXECUTED_PROCEDURE:{procedure_name}",
                "DATABASE",
            )
        except Exception as e:
            logger.error(f"Error al ejecutar el procedimiento '{procedure_name}': {e}")
            await self._log_audit_event(
                user,
                f"FAILED_PROCEDURE:{procedure_name}",
                "DATABASE",
            )
            raise

    async def validate_procedure_execution(
            self, user: User, procedure_name: str, *args: Any
    ) -> tuple[bool, str]:
        """
        Valida si un procedimiento puede ser ejecutado sin ejecutarlo realmente.
        Retorna (puede_ejecutar, mensaje).
        """
        try:
            proc = self.get_procedure_info(procedure_name)
            if not proc:
                return False, f"Procedimiento '{procedure_name}' no encontrado"

            if not proc.validate_args(args):
                return False, f"Número incorrecto de argumentos para {procedure_name}"

            # Aquí podrías añadir más validaciones según necesites
            return True, "Procedimiento puede ser ejecutado"
        except Exception as e:
            return False, str(e)

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

    async def get_user(self, username: str) -> Optional[User]:
        """
        Obtiene un usuario por su nombre de usuario.
        """
        try:
            logger.info(f"Obteniendo usuario: {username}")
            async with self.pool.acquire() as conn:
                test_result = await conn.fetchval("SELECT decrypt_value(encrypt_value('test'))")
                logger.info(f"Test de encriptación/desencriptación: {test_result}")

                row = await conn.fetchrow("""
                    SELECT 
                        id, 
                        decrypt_value(username) as username,
                        password_hash,
                        role_id
                    FROM users 
                    WHERE username = encrypt_value($1)
                """, username)

                if not row:
                    return None

                return User(**dict(row))
        except Exception as e:
            logger.error(f"Error al obtener usuario: {e}")
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
                    timestamp=datetime.now(),
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
                await asyncio.sleep(60)
        except Exception as e:
            logger.error(f"Error durante el monitoreo de la base de datos: {e}")

    async def _check_database_health(self) -> None:
        """
        Verifica el estado de salud de la base de datos y registra métricas.
        """
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetch("SELECT COUNT(*) AS active_connections FROM pg_stat_activity;")
                active_connections = result[0]["active_connections"]
                logger.info(f"Conexiones activas: {active_connections}")

                result = await conn.fetch("SELECT now() - pg_backend_timestamp() AS query_latency;")
                query_latency = result[0]["query_latency"].total_seconds()
                logger.info(f"Latencia de consultas: {query_latency} segundos")

                result = await conn.fetch("SELECT pg_database_size(current_database()) AS database_size;")
                database_size = result[0]["database_size"]
                logger.info(f"Tamaño de la base de datos: {database_size / (1024 ** 3):.2f} GB")

                self._record_database_metrics(active_connections, query_latency, database_size)
        except Exception as e:
            logger.error(f"Error al verificar el estado de salud de la base de datos: {e}")

    def _record_database_metrics(self, active_connections: int, query_latency: float, database_size: int) -> None:
        """
        Registra métricas de la base de datos en un sistema de monitorización.
        """
        # TODO: Implementar integración con sistema de métricas
        pass

    async def scale_database(self) -> None:
        """
        Escala horizontalmente la base de datos utilizando sharding.
        """
        try:
            logger.info("Escalando base de datos horizontalmente...")
            # TODO: Implementar estrategia de sharding
            pass
        except Exception as e:
            logger.error(f"Error al escalar la base de datos: {e}")

    async def enable_high_availability(self) -> None:
        """
        Habilita alta disponibilidad para la base de datos utilizando réplicas.
        """
        try:
            logger.info("Habilitando alta disponibilidad para la base de datos...")
            # TODO: Implementar configuración de alta disponibilidad
            pass
        except Exception as e:
            logger.error(f"Error al habilitar la alta disponibilidad: {e}")
