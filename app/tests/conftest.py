import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from pathlib import Path
import sys 
from httpx import ASGITransport, AsyncClient

sys.path.append(str(Path(__file__).parent.parent.parent))

from app.main import app
from app.db.database import get_db


POSTGRES_HOST='localhost'
POSTGRES_PORT=5432
POSTGRES_USER='postgres'
POSTGRES_PASSWORD=1234
POSTGRES_DB='test_sudoku'

TEST_DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"


@pytest_asyncio.fixture
async def engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=True,
    )

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def session(engine):
    connection = await engine.connect()
    transaction = await connection.begin()

    async_session = async_sessionmaker(
        bind=connection,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    session = async_session()

    yield session

    await session.close()
    await transaction.rollback()

    await connection.close()
    await connection.close()


@pytest_asyncio.fixture
async def async_client(session):
    async def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as async_test_client:
        yield async_test_client

