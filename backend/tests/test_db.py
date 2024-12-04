import pytest
from sqlalchemy import select
from backend.db.models import School


@pytest.mark.asyncio
async def test_database_connection(db_session):
    """Verifica que podemos conectar y consultar la base de datos"""
    # Consultar las escuelas insertadas en los datos iniciales
    result = await db_session.execute(select(School))
    schools = result.scalars().all()

    # Verificar que tenemos las dos escuelas iniciales
    assert len(schools) == 2
    assert any(school.name == "IES San Isidro" for school in schools)
    assert any(school.name == "Lincoln High School" for school in schools)