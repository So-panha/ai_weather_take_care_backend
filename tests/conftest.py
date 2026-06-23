import pytest
from httpx import AsyncClient, ASGITransport
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator

from app.main import app
from app.database.base import Base
from app.database.session import get_db

# Use an in-memory SQLite DB for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(TEST_DATABASE_URL, echo=False)
async_session_maker_test = async_sessionmaker(
    engine_test, class_=AsyncSession, expire_on_commit=False, autoflush=False
)

async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker_test() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture(autouse=True)
async def init_models():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
