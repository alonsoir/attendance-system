"""
This package manages the database and API-related operations.
"""

from backend.api.endpoints import websocket_router, whatsapp_router
from backend.core.config import Settings, get_settings

__version__ = "0.1.0"

__all__ = [
    "Settings",
    "get_settings",
    "websocket_router",
    "whatsapp_router",
    "__version__",
]
