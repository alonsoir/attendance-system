import logging

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from backend.core.config import settings
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.declarative import declared_attr

logger = logging.getLogger(__name__)

class Base:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

Base = declarative_base(cls=Base)

# Import models here to ensure they're registered

from .models import User, Interaction, ServiceStatus, InteractionMessage



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
                from backend.core.security import get_password_hash

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
