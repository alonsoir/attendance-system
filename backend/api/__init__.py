"""
This package manages API-related operations.
"""
from fastapi import FastAPI

from backend.core.config import settings
from backend.db.base import initialize_db

from .endpoints import websocket_router, whatsapp_router


def create_app():
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
    )

    initialize_db()

    app.include_router(
        websocket_router,
        prefix=settings.API_V1_STR,
    )

    app.include_router(
        whatsapp_router,
        prefix=settings.API_V1_STR,
    )

    return app
