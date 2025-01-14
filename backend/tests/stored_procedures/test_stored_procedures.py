import datetime
import logging
from datetime import date

import pytest

from backend.db.models_acl import User
from backend.tests.utils.docker_check import check_docker

logger = logging.getLogger(__name__)

pytestmark = pytest.mark.skipif(
    not check_docker(), reason="Docker no está disponible o no está corriendo"
)


@pytest.mark.asyncio
async def test_create_school(db_session, school_user: User):
    logger.info("Probando creación de escuela")

    test_school = {
        "name": "Test School",
        "phone": "+34666777888",
        "address": "Test Address 123",
        "state": "Madrid",  # Añadido state
        "country": "ES",  # Código de país de 5 caracteres o menos
    }

    school_id = None  # Para el parámetro INOUT

    async with db_session.transaction(school_user) as conn:
        await conn.execute(
            """
            CALL create_school($1, $2, $3, $4, $5, $6, $7)
            """,
            test_school["name"],
            test_school["phone"],
            test_school["address"],
            test_school["state"],
            test_school["country"],
            school_user.id if school_user else None,  # created_by
            school_id  # INOUT parameter para recibir el ID generado
        )

        # Verificar que la escuela existe y tiene los datos correctos
        schools = await conn.fetch(
            """
            SELECT * FROM schools 
            WHERE name = $1 
            AND phone = $2 
            AND address = $3 
            AND state = $4 
            AND country = $5
            """,
            test_school["name"],
            test_school["phone"],
            test_school["address"],
            test_school["state"],
            test_school["country"]
        )

        assert len(schools) == 1, "La escuela creada no se encuentra en la base de datos"


@pytest.mark.asyncio
async def test_search_messages(db_session, school_user: User):
    logger.info("Probando búsqueda de mensajes con Full Text Search")

    # Primero insertamos algunos mensajes de prueba
    test_messages = [
        "El estudiante ha completado su tarea de matemáticas",
        "Reunión con el tutor para discutir el progreso",
        "matemáticas avanzadas y ejercicios de álgebra",
        "Clase de historia programada para mañana"
    ]

    async with db_session.transaction(school_user) as conn:
        # Insertar mensajes de prueba
        for content in test_messages:
            await conn.execute(
                """
                INSERT INTO messages (
                    claude_conversation_id, 
                    content, 
                    sender_type, 
                    created_at
                ) VALUES ($1, $2, $3, $4)
                """,
                'test-conv-1',
                content,
                'CLAUDE',
                datetime.now(datetime.timezone.utc)
            )

        # Probar búsqueda
        results = await conn.fetch(
            """
            SELECT * FROM search_messages($1)
            """,
            'matemáticas'
        )

        # Verificaciones
        assert len(results) == 2, "Debería encontrar 2 mensajes con 'matemáticas'"

        # Verificar ranking
        assert results[0]['rank'] > results[1]['rank'], "El primer resultado debería tener mayor relevancia"

        # Buscar con otros filtros
        results = await conn.fetch(
            """
            SELECT * FROM search_messages($1, $2, $3, $4, $5, $6)
            """,
            'matemáticas',  # texto a buscar
            None,  # student_id
            None,  # school_id
            None,  # tutor_id
            datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1),  # from_date
            datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)  # to_date
        )

        assert len(results) == 2, "La búsqueda con filtros de fecha debería funcionar"

@pytest.mark.asyncio
async def test_update_encrypted_school(db_session, admin_user: User):
    logger.info("Probando actualización de escuela encriptada")

    # Crear escuela para prueba
    test_school = {
        "name": "Test School Salesianos",
        "phone": "+34666777999",
        "address": "Test Address 456",
        "country": "Spain",
    }

    async with db_session.transaction(admin_user) as conn:
        await conn.execute(
            """
            CALL create_school($1, $2, $3, $4, $5)
            """,
            test_school["name"],
            test_school["phone"],
            test_school["address"],
            test_school["country"],
            None,
        )

        # Encontrar la escuela creada
        schools = await conn.fetch("SELECT * FROM get_all_encrypted_schools()")
        school = next(
            s
            for s in schools
            if s["name"] == test_school["name"] and s["phone"] == test_school["phone"]
        )

        # Actualizar la escuela
        updated_data = {
            "name": "Updated School Name",
            "phone": "+34777888999",
            "address": "Updated Address",
            "country": "France",
        }

        await conn.execute(
            """
            CALL update_encrypted_school($1, $2, $3, $4, $5)
            """,
            school["id"],
            updated_data["name"],
            updated_data["phone"],
            updated_data["address"],
            updated_data["country"],
        )

        # Verificar la actualización
        updated_schools = await conn.fetch(
            "SELECT * FROM get_encrypted_school($1)", school["id"]
        )
        updated_school = dict(updated_schools[0])
        assert updated_school["name"] == updated_data["name"]
        assert updated_school["phone"] == updated_data["phone"]
        assert updated_school["address"] == updated_data["address"]
        assert updated_school["country"] == updated_data["country"]


@pytest.mark.asyncio
async def test_delete_school(db_session, admin_user: User):
    logger.info("Probando eliminación de escuela")

    test_school = {
        "name": "School To Delete",
        "phone": "+34666777888",
        "address": "Delete Address 123",
        "country": "Spain",
    }

    async with db_session.transaction(admin_user) as conn:
        await conn.execute(
            """
            CALL create_school($1, $2, $3, $4, $5)
            """,
            test_school["name"],
            test_school["phone"],
            test_school["address"],
            test_school["country"],
            None,
        )

        # Encontrar la escuela creada
        schools = await conn.fetch("SELECT * FROM get_all_encrypted_schools()")
        school = next(
            s
            for s in schools
            if s["name"] == test_school["name"] and s["phone"] == test_school["phone"]
        )

        # Eliminar la escuela
        await conn.execute("CALL delete_school($1)", school["id"])

        # Verificar que la escuela ya no existe
        deleted_school = await conn.fetch(
            "SELECT * FROM get_encrypted_school($1)", school["id"]
        )
        assert len(deleted_school) == 0, "La escuela no se eliminó correctamente"


@pytest.mark.asyncio
async def test_tutor_crud(db_session, admin_user: User):
    logger.info("Probando operaciones CRUD de tutor")

    test_tutor = {
        "name": "Test Tutor",
        "phone": "+34666555444",
        "email": "test.tutor@test.com",
    }

    async with db_session.transaction(admin_user) as conn:
        # Crear tutor
        await conn.execute(
            """
            CALL create_tutor($1, $2, $3, $4)
            """,
            test_tutor["name"],
            test_tutor["phone"],
            test_tutor["email"],
            None,
        )

        # Verificar creación
        tutors = await conn.fetch("SELECT * FROM get_all_encrypted_tutors()")
        tutor = next(
            t
            for t in tutors
            if t["name"] == test_tutor["name"] and t["email"] == test_tutor["email"]
        )
        assert tutor is not None, "El tutor no se creó correctamente"

        # Actualizar tutor
        updated_data = {
            "name": "Updated Tutor",
            "phone": "+34777666555",
            "email": "updated.tutor@test.com",
        }

        await conn.execute(
            """
            CALL update_encrypted_tutor($1, $2, $3, $4)
            """,
            tutor["id"],
            updated_data["name"],
            updated_data["phone"],
            updated_data["email"],
        )

        # Verificar actualización
        updated_tutor = await conn.fetch(
            "SELECT * FROM get_encrypted_tutor($1)", tutor["id"]
        )
        updated_tutor = dict(updated_tutor[0])
        assert updated_tutor["name"] == updated_data["name"]
        assert updated_tutor["phone"] == updated_data["phone"]
        assert updated_tutor["email"] == updated_data["email"]

        # Eliminar tutor
        await conn.execute("CALL delete_tutor($1)", tutor["id"])

        # Verificar eliminación
        deleted_tutor = await conn.fetch(
            "SELECT * FROM get_encrypted_tutor($1)", tutor["id"]
        )
        assert len(deleted_tutor) == 0, "El tutor no se eliminó correctamente"


@pytest.mark.asyncio
async def test_student_and_relationships(db_session, admin_user: User):
    logger.info("Probando estudiantes y relaciones")

    async with db_session.transaction(admin_user) as conn:
        # Crear escuela
        school_data = {
            "name": "Test School",
            "phone": "+34666777888",
            "address": "Test Address",
            "country": "Spain",
        }
        await conn.execute(
            """
            CALL create_school($1, $2, $3, $4, $5)
            """,
            school_data["name"],
            school_data["phone"],
            school_data["address"],
            school_data["country"],
            None,
        )

        schools = await conn.fetch("SELECT * FROM get_all_encrypted_schools()")
        school = next(s for s in schools if s["name"] == school_data["name"])

        # Crear tutor
        tutor_data = {
            "name": "Test Tutor",
            "phone": "+34666555444",
            "email": "test.tutor@test.com",
        }
        await conn.execute(
            """
            CALL create_tutor($1, $2, $3, $4)
            """,
            tutor_data["name"],
            tutor_data["phone"],
            tutor_data["email"],
            None,
        )

        tutors = await conn.fetch("SELECT * FROM get_all_encrypted_tutors()")
        tutor = next(t for t in tutors if t["name"] == tutor_data["name"])

        # Crear estudiante
        await conn.execute(
            """
            CALL create_student($1, $2, $3, $4)
            """,
            "Test Student",
            date(2010, 1, 1),
            school["id"],
            None,
        )

        students = await conn.fetch("SELECT * FROM get_all_encrypted_students()")
        student = next(s for s in students if s["name"] == "Test Student")

        # Crear relación tutor-estudiante
        await conn.execute(
            """
            CALL create_tutor_student_relationship($1, $2, $3)
            """,
            tutor["id"],
            student["id"],
            "PARENT",
        )

        # Verificar relación
        relationships = await conn.fetch(
            "SELECT * FROM get_student_tutors($1)", student["id"]
        )
        assert len(relationships) > 0, "No se encontró la relación tutor-estudiante"
        relationship = dict(relationships[0])
        assert relationship["relationship_type"] == "PARENT"


@pytest.mark.asyncio
async def test_permissions_and_roles(
    db_session, admin_user: User, school_user: User, tutor_user: User
):
    logger.info("Probando permisos y roles")

    async with db_session.transaction() as conn:
        # Verificar permisos de admin
        has_create_school = await conn.fetchval(
            "SELECT user_has_permission($1, $2)", admin_user.id, "CREATE_SCHOOL"
        )
        assert has_create_school, "Admin debería tener permiso CREATE_SCHOOL"

        # Verificar permisos de escuela
        has_create_student = await conn.fetchval(
            "SELECT user_has_permission($1, $2)", school_user.id, "CREATE_STUDENT"
        )
        assert has_create_student, "School user debería tener permiso CREATE_STUDENT"

        # Verificar permisos de tutor
        has_view_records = await conn.fetchval(
            "SELECT user_has_permission($1, $2)", tutor_user.id, "VIEW_STUDENT_RECORDS"
        )
        assert has_view_records, "Tutor debería tener permiso VIEW_STUDENT_RECORDS"

        # Verificar permisos negativos
        has_admin_permission = await conn.fetchval(
            "SELECT user_has_permission($1, $2)", tutor_user.id, "CREATE_SCHOOL"
        )
        assert not has_admin_permission, "Tutor no debería tener permiso CREATE_SCHOOL"
