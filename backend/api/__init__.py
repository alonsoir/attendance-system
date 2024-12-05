"""
This package manages API-related operations.
"""
from fastapi import FastAPI

from backend.core.config import get_settings
from backend.db.base import db

from .endpoints import websocket_router, whatsapp_router

settings = get_settings()


def create_app():
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
    )

    db.initialize_db()

    app.include_router(
        websocket_router,
        prefix=settings.API_V1_STR,
    )

    app.include_router(
        whatsapp_router,
        prefix=settings.API_V1_STR,
    )

    return app
