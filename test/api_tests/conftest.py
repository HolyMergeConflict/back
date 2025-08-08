from unittest.mock import patch, MagicMock

import pytest
from httpx import AsyncClient
from httpx import ASGITransport  # Вот ключевой компонент
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.models.base_db_models import Base
from app.database import get_db, engine
from app.main import app  # замени, если у тебя приложение где-то в другом месте

DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="session")
async def async_engine():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture(scope="function")
async def db_session(async_engine):
    async_session = async_sessionmaker(bind=async_engine, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture
async def client(db_session: AsyncSession):
    transport = ASGITransport(app=app)

    app.dependency_overrides[get_db] = lambda: db_session

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(autouse=True)
def mock_redis():
    mock = MagicMock()
    mock.get.return_value = None
    mock.set.return_value = True
    mock.exists.return_value = False
    mock.expire.return_value = True

    with patch("app.services.auth_service.redis_client", mock), \
            patch("app.middleware.auth_middleware.redis_client", mock):
        yield mock