"""
This module contains the database models and the database session.
"""
from backend.core.config import get_settings

from .base import Base, initialize_db
from .models import Interaction, User
from .session import (
    async_engine,
    check_database_connection,
    get_db,
    get_db_context,
    init_db,
)

settings = get_settings()
__all__ = [
    "Base",
    "initialize_db",
    "User",
    "Interaction",
    "async_engine",
    "get_db",
    "get_db_context",
    "check_database_connection",
    "init_db",
    "settings",
]
