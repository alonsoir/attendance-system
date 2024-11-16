import logging

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from backend.core.config import settings

logger = logging.getLogger(__name__)


class Base:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


Base = declarative_base(cls=Base)


def initialize_db():
    """
    Inicializa la base de datos y crea todas las tablas necesarias.
    """
    from .models import (
        User,
        ServiceStatus,
        Interaction,
        InteractionMessage,
    )  # Importar todos los modelos

    try:
        engine = create_engine(settings.DATABASE_URL)
        Base.metadata.create_all(bind=engine)
        logger.info("Base de datos inicializada correctamente")

        # Crear usuario administrador por defecto si no existe
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()

        try:
            # Verificar y crear usuario admin
            admin_exists = db.query(User).filter(User.username == "admin").first()
            if not admin_exists:
                from backend.core.security import get_password_hash

                admin_user = User(
                    username="admin",
                    email="admin@example.com",
                    hashed_password=get_password_hash("admin"),
                    is_superuser=True,
                )
                db.add(admin_user)

            # Verificar y crear estados de servicio iniciales
            service_status = db.query(ServiceStatus).first()
            if not service_status:
                services = [
                    ServiceStatus(service_name="claude", status=True),
                    ServiceStatus(service_name="meta", status=True),
                ]
                db.bulk_save_objects(services)

            db.commit()
            logger.info("Base de datos inicializada con datos por defecto")

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error inicializando la base de datos: {str(e)}")
        raise
