import logging

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from attendance_system.core.config import settings

logger = logging.getLogger(__name__)

# Crear base declarativa para los modelos SQLAlchemy
Base = declarative_base()


def initialize_db():
    """
    Inicializa la base de datos y crea todas las tablas necesarias.
    """
    from .models import Interaction, User  # Importación aquí para evitar ciclos

    try:
        engine = create_engine(settings.DATABASE_URL)
        Base.metadata.create_all(bind=engine)
        logger.info("Base de datos inicializada correctamente")

        # Crear usuario administrador por defecto si no existe
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()

        try:
            admin_exists = db.query(User).filter(User.username == "admin").first()
            if not admin_exists:
                from attendance_system.core.security import get_password_hash

                admin_user = User(
                    username="admin",
                    email="admin@example.com",
                    hashed_password=get_password_hash("admin"),
                    is_superuser=True,
                )
                db.add(admin_user)
                db.commit()
                logger.info("Usuario administrador creado")
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error inicializando la base de datos: {str(e)}")
        raise
