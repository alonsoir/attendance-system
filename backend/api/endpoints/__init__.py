"""
This module contains the FastAPI router instances.
"""
from .websocket import router as websocket_router
from .whatsapp import router as whatsapp_router

__all__ = ["websocket_router", "whatsapp_router"]