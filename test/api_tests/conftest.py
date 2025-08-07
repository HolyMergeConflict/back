import pytest
from httpx import AsyncClient
from httpx import ASGITransport  # Вот ключевой компонент
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.models.base_db_models import Base
from app.database import get_db
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

@pytest.fixture(scope="function")
async def client(db_session: AsyncSession):
    app.dependency_overrides[get_db] = lambda: db_session

    transport = ASGITransport(app=app)  # Ключевой момент
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
