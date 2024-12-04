import asyncio
import pytest
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from .containers.postgres import PostgresTestContainer

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def postgres_container() -> AsyncGenerator[PostgresTestContainer, None]:
    """Proporciona un contenedor PostgreSQL para las pruebas"""
    container = PostgresTestContainer()
    await container.start()
    yield container
    await container.stop()

@pytest.fixture(scope="function")
async def db_session(postgres_container: PostgresTestContainer) -> AsyncGenerator[AsyncSession, None]:
    """Proporciona una sesión de base de datos para cada test"""
    async for session in postgres_container.get_session():
        yield session