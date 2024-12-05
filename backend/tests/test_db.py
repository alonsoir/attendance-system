import logging

import pytest
from sqlalchemy import select

from backend.db.models import School
from backend.tests.utils.docker_check import check_docker

logger = logging.getLogger(__name__)

pytestmark = pytest.mark.skipif(
    not check_docker(),
    reason="Docker no está disponible o no está corriendo"
)

@pytest.mark.asyncio
async def test_connection_details(postgres_container):
    logger.info("Probando detalles de conexión")
    url = postgres_container.client.api.base_url
    logger.info(f"URL de conexión: {url}")
    assert url is not None

@pytest.mark.asyncio
async def test_school_creation(postgres_container,db_session):
    """Test de creación de escuela"""
    logger.info("Ejecutando test de creación de escuela")
    result = await db_session.execute(select(School))
    schools = result.scalars().all()
    logger.info(f"Encontradas {len(schools)} escuelas")
    assert len(schools) == 2

@pytest.mark.asyncio
async def test_database_connection(db_session):
    """Verifica que podemos conectar y consultar la base de datos"""
    logger.info("Verificando conexión a base de datos")
    result = await db_session.execute(select(School))
    schools = result.scalars().all()

    logger.info(f"Verificando {len(schools)} escuelas encontradas")
    assert len(schools) == 2
    assert any(school.name == "IES San Isidro" for school in schools)
    assert any(school.name == "Lincoln High School" for school in schools)