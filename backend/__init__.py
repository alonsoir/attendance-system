"""
This package manages the database and API-related operations.
"""

from backend.api.endpoints import websocket_router, whatsapp_router

__version__ = "0.1.0"

__all__ = [
    "websocket_router",
    "whatsapp_router",
    "__version__",
]
