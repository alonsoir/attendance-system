import logging

import pytest

from backend.db.models_acl import User
from backend.tests.utils.docker_check import check_docker

logger = logging.getLogger(__name__)

pytestmark = pytest.mark.skipif(
    not check_docker(),
    reason="Docker no está disponible o no está corriendo"
)


@pytest.mark.asyncio
async def test_create_encrypted_school(db_session, admin_user: User):
    logger.info("Probando creación de escuela encriptada")

    school_id = None
    test_school = {
        "name": "Test School",
        "phone": "+34666777888",
        "address": "Test Address 123",
        "country": "Spain"
    }

    # CREATE
    await db_session.execute_procedure(
        admin_user,
        "create_school",
        test_school["name"],
        test_school["phone"],
        test_school["address"],
        test_school["country"],
        school_id
    )

    # READ y verificación
    async with db_session.pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT 
                id,
                decrypt_value(name) as name,
                decrypt_value(phone) as phone,
                decrypt_value(address) as address,
                decrypt_value(country) as country
            FROM schools
        """)

        schools = [dict(row) for row in rows]

        # Verificar que nuestra escuela de prueba existe en la base de datos
        assert any(
            school["name"] == test_school["name"] and
            school["phone"] == test_school["phone"] and
            school["address"] == test_school["address"] and
            school["country"] == test_school["country"]
            for school in schools
        ), "La escuela de prueba no se encontró en la base de datos"

@pytest.mark.asyncio
async def test_update_encrypted_school(db_session, admin_user: User):
    logger.info("Probando actualización de escuela encriptada")

    # CREATE
    school_id = None
    test_school = {
        "name": "Test School Salesianos",
        "phone": "+34666777999",
        "address": "Test Address 456",
        "country": "Spain"
    }

    # CREATE
    await db_session.execute_procedure(
        admin_user,
        "create_school",
        test_school["name"],
        test_school["phone"],
        test_school["address"],
        test_school["country"],
        school_id
    )

    await db_session.commit()

    schools = await db_session.get_schools(admin_user)
    assert len(schools) == 1
    school_id = schools[0]["id"]

    # UPDATE
    await db_session.execute_procedure(admin_user, "update_encrypted_school",
                                      school_id, "Updated School Name", "+34777888999", "Updated Address", "France")
    await db_session.commit()

    updated_schools = await db_session.get_schools(admin_user)
    assert updated_schools[0]["name"] == 'Updated School Name'
    assert updated_schools[0]["phone"] == '+34777888999'
    assert updated_schools[0]["address"] == 'Updated Address'
    assert updated_schools[0]["country"] == 'France'


@pytest.mark.asyncio
async def test_delete_school(db_session, admin_user: User):
    logger.info("Probando eliminación de escuela")

    # CREATE
    await db_session.execute_procedure(admin_user, "create_encrypted_school",
                                      "Test School", "+34666777888", "Test Address 123", "Spain")
    await db_session.commit()

    schools = await db_session.get_schools(admin_user)
    assert len(schools) == 1
    school_id = schools[0]["id"]

    # DELETE
    await db_session.execute_procedure(admin_user, "delete_school", school_id)
    await db_session.commit()

    deleted_schools = await db_session.get_schools(admin_user)
    assert len(deleted_schools) == 0


@pytest.mark.asyncio
async def test_permissions_and_roles(db_session, admin_user: User, school_user: User, tutor_user: User):
    logger.info("Probando permisos y roles")

    # Verificar permisos de admin
    assert await db_session.has_permission(admin_user, "CREATE_SCHOOL")
    assert await db_session.has_permission(admin_user, "UPDATE_SCHOOL")
    assert await db_session.has_permission(admin_user, "DELETE_SCHOOL")

    # Verificar permisos de escuela
    assert await db_session.has_permission(school_user, "CREATE_STUDENT")
    assert await db_session.has_permission(school_user, "UPDATE_STUDENT")
    assert await db_session.has_permission(school_user, "SEND_MESSAGES")
    assert not await db_session.has_permission(school_user, "DELETE_SCHOOL")

    # Verificar permisos de tutor
    assert await db_session.has_permission(tutor_user, "VIEW_STUDENT_RECORDS")
    assert await db_session.has_permission(tutor_user, "SEND_MESSAGES")
    assert not await db_session.has_permission(tutor_user, "CREATE_SCHOOL")