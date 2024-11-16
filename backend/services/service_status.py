from backend.db.models import ServiceStatus
from backend.db.session import SessionLocal


async def check_service_status(service_name: str) -> bool:
    """Checks if a service is available"""
    db = SessionLocal()
    try:
        status = db.query(ServiceStatus).filter_by(service_name=service_name).first()
        return status.status if status else False
    finally:
        db.close()
