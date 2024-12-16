import logging
from datetime import date

import pytest
from sqlalchemy import select

from backend.db.models import School
from backend.tests.utils.docker_check import check_docker

logger = logging.getLogger(__name__)

pytestmark = pytest.mark.skipif(
    not check_docker(), reason="Docker no está disponible o no está corriendo"
)


@pytest.mark.asyncio
async def test_connection_details(postgres_container):
    logger.info("Probando detalles de conexión")
    container, port = postgres_container  # Desempaquetar la tupla
    url = container.client.api.base_url
    logger.info(f"URL de conexión: {url} port: {port}")
    assert url is not None
    assert port is not None


import uuid

import pytest
from sqlalchemy import text


@pytest.mark.asyncio
async def test_schema_creation(db_session):
    """Verifica que todas las tablas se han creado correctamente"""
    logger.info("Verificando creación de tablas")

    # Primero verificamos que estamos conectados
    result = await db_session.execute(text("SELECT current_database()"))
    db_name = result.scalar()
    logger.info(f"Conectado a base de datos: {db_name}")

    tables = [
        "schools",
        "tutors",
        "students",
        "tutor_student",
        "conversations",
        "messages",
        "service_status",
    ]

    for table in tables:
        logger.info(f"Verificando existencia de tabla: {table}")
        result = await db_session.execute(
            text(
                f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')"
            )
        )
        exists = result.scalar()
        logger.info(f"Tabla {table} existe: {exists}")
        assert exists, f"La tabla {table} no existe"


@pytest.mark.asyncio
async def test_school_crud_operations(db_session):
    """Prueba operaciones CRUD básicas en la tabla schools"""
    logger.info("Probando operaciones CRUD en schools")

    # CREATE
    school_id = str(uuid.uuid4())
    await db_session.execute(
        text(
            """
        INSERT INTO schools (id, name, phone, address, country)
        VALUES (:id, :name, :phone, :address, :country)
        """
        ),
        {
            "id": school_id,
            "name": "Test School",
            "phone": "+34666777888",
            "address": "Test Address 123",
            "country": "Spain",
        },
    )
    await db_session.commit()

    # READ
    result = await db_session.execute(
        text("SELECT * FROM schools WHERE id = :id"), {"id": school_id}
    )
    school = result.fetchone()
    assert school.name == "Test School"
    assert school.phone == "+34666777888"
    assert school.address == "Test Address 123"
    assert school.country == "Spain"

    # UPDATE
    await db_session.execute(
        text("UPDATE schools SET name = :name WHERE id = :id"),
        {"id": school_id, "name": "Updated School Name"},
    )
    await db_session.commit()

    result = await db_session.execute(
        text("SELECT name FROM schools WHERE id = :id"), {"id": school_id}
    )
    updated_name = result.fetchone()[0]
    assert updated_name == "Updated School Name"

    # DELETE
    await db_session.execute(
        text("DELETE FROM schools WHERE id = :id"), {"id": school_id}
    )
    await db_session.commit()

    result = await db_session.execute(
        text("SELECT COUNT(*) FROM schools WHERE id = :id"), {"id": school_id}
    )
    count = result.scalar()
    assert count == 0
    logger.info("Prueba de operaciones CRUD en schools completada")


@pytest.mark.asyncio
async def test_relationships(db_session):
    """Prueba las relaciones entre tablas"""
    logger.info("Probando relaciones entre tablas")

    # Crear una escuela
    school_id = str(uuid.uuid4())
    await db_session.execute(
        text(
            """
        INSERT INTO schools (id, name, phone, address, country)
        VALUES (:id, :name, :phone, :address, :country)
        """
        ),
        {
            "id": school_id,
            "name": "Test School",
            "phone": "+34666777888",
            "address": "Test Address 123",
            "country": "Spain",
        },
    )

    # Crear un estudiante asociado a la escuela
    student_id = str(uuid.uuid4())
    await db_session.execute(
        text(
            """
        INSERT INTO students (id, name, date_of_birth, school_id)
        VALUES (:id, :name, :dob, :school_id)
        """
        ),
        {
            "id": student_id,
            "name": "Test Student",
            "dob": date(2010, 1, 1),
            "school_id": school_id,
        },
    )
    await db_session.commit()

    # Verificar la relación
    result = await db_session.execute(
        text(
            """
        SELECT s.name as student_name, sch.name as school_name
        FROM students s
        JOIN schools sch ON s.school_id = sch.id
        WHERE s.id = :student_id
        """
        ),
        {"student_id": student_id},
    )
    row = result.fetchone()
    assert row.student_name == "Test Student"
    assert row.school_name == "Test School"


@pytest.mark.asyncio
async def test_constraints(db_session):
    """Prueba las restricciones de la base de datos"""
    logger.info("Probando restricciones de la base de datos")

    # Probar restricción UNIQUE en phone de schools
    school_id1 = str(uuid.uuid4())
    school_id2 = str(uuid.uuid4())

    await db_session.execute(
        text(
            """
        INSERT INTO schools (id, name, phone, address, country)
        VALUES (:id, :name, :phone, :address, :country)
        """
        ),
        {
            "id": school_id1,
            "name": "Test School 1",
            "phone": "+34666777888",
            "address": "Test Address 123",
            "country": "Spain",
        },
    )
    await db_session.commit()

    # Intentar insertar otra escuela con el mismo teléfono
    with pytest.raises(Exception) as exc_info:
        await db_session.execute(
            text(
                """
            INSERT INTO schools (id, name, phone, address, country)
            VALUES (:id, :name, :phone, :address, :country)
            """
            ),
            {
                "id": school_id2,
                "name": "Test School 2",
                "phone": "+34666777888",  # Mismo teléfono
                "address": "Test Address 456",
                "country": "Spain",
            },
        )
        await db_session.commit()

    assert "duplicate key value violates unique constraint" in str(exc_info.value)


@pytest.mark.asyncio
async def test_school_creation(db_session):
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
    assert any(school.name == "IES Test Madrid" for school in schools)
    assert any(school.name == "Test High School" for school in schools)
