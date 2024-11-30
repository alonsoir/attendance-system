import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

import uvicorn
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.core.app import app, settings
from backend.api.endpoints import websocket_router, whatsapp_router
from backend.db.session import check_database_connection, init_db
from backend.services import AttendanceManager

# Configurar logging
logger = logging.getLogger("backend")

@asynccontextmanager
async def lifespan(app):
    """
    Contexto de vida de la aplicación.
    Se ejecuta al inicio y cierre del servidor.
    """
    # Startup
    logger.info("Iniciando sistema de gestión de asistencia...")

    # Inicializar base de datos
    try:
        await init_db()
        logger.info("Base de datos inicializada correctamente")
    except Exception as e:
        logger.error(f"Error inicializando la base de datos: {str(e)}")
        raise

    # Verificar servicios externos
    try:
        service_status = await AttendanceManager.check_service_status()
        logger.info(f"Estado de servicios externos: {json.dumps(service_status)}")
    except Exception as e:
        logger.warning(f"Error verificando servicios externos: {str(e)}")

    yield

    # Shutdown
    logger.info("Cerrando sistema de gestión de asistencia...")

# Asignar el lifespan a la app
app.router.lifespan_context = lifespan

# Middleware para logging de requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.utcnow()
    response = await call_next(request)
    end_time = datetime.utcnow()

    logger.info(
        f"Request: {request.method} {request.url.path} "
        f"Status: {response.status_code} "
        f"Duration: {(end_time - start_time).total_seconds():.3f}s"
    )

    return response

# Manejador de errores global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error no manejado: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )

# Montar rutas
app.include_router(websocket_router, prefix=settings.API_V1_STR, tags=["websocket"])
app.include_router(whatsapp_router, prefix=settings.API_V1_STR, tags=["whatsapp"])

# Montar archivos estáticos
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Endpoints de estado y monitoreo
@app.get("/health")
async def health_check():
    """Verificar estado del sistema"""
    db_status = await check_database_connection()
    service_status = await AttendanceManager.check_service_status()

    status_ok = db_status and all(service_status.values())

    return {
        "status": "healthy" if status_ok else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION,
        "services": {
            "database": "online" if db_status else "offline",
            **service_status,
        },
    }

@app.get("/metrics")
async def get_metrics():
    """Obtener métricas del sistema"""
    if not settings.ENABLE_METRICS:
        raise HTTPException(status_code=404, detail="Metrics not enabled")

    # Implementar recolección de métricas aquí
    return {"message": "Metrics endpoint"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )