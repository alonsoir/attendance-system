from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from attendance_system.core.config import settings
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

# Crear el motor de la base de datos
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verifica la conexión antes de usarla
    pool_size=5,  # Número máximo de conexiones en el pool
    max_overflow=10  # Número máximo de conexiones que se pueden crear más allá del pool_size
)

# Crear el fabricante de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db():
    """
    Contexto para manejar sesiones de base de datos.
    Asegura que la sesión se cierre después de su uso.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_context():
    """
    Versión sin decorador del get_db para uso en dependencias FastAPI
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def check_database_connection():
    """
    Verifica la conexión a la base de datos
    """
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Error conectando a la base de datos: {str(e)}")
        return False
    finally:
        db.close()


def init_db():
    """
    Inicializa la base de datos con datos iniciales si es necesario
    """
    from attendance_system.db.models import User, ServiceStatus

    db = SessionLocal()
    try:
        # Verificar si ya existen registros de estado de servicio
        service_status = db.query(ServiceStatus).first()
        if not service_status:
            # Crear registros iniciales de estado de servicio
            services = [
                ServiceStatus(service_name="claude", status=True),
                ServiceStatus(service_name="meta", status=True)
            ]
            db.bulk_save_objects(services)
            db.commit()
            logger.info("Estados de servicio iniciales creados")

    except Exception as e:
        logger.error(f"Error inicializando la base de datos: {str(e)}")
        db.rollback()
    finally:
        db.close()