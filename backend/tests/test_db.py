import pytest
from sqlalchemy import select

from backend.db.models import School
from backend.tests.utils.docker_check import check_docker


@pytest.mark.skipif(not check_docker(), reason="Docker no está disponible o no está corriendo")
class TestDatabaseOperations:

    @pytest.mark.asyncio
    async def test_connection_details(postgres_container):
        url = postgres_container.get_connection_url()
        print(f"URL de conexión: {url}")
        assert url is not None

    @pytest.mark.asyncio
    async def test_school_creation(db_session):
        """Test de creación de escuela"""
        # El schema ya está creado y hay datos de prueba disponibles
        result = await db_session.execute(select(School))
        schools = result.scalars().all()
        assert len(schools) == 2  # Verificamos que tenemos las dos escuelas de prueba

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