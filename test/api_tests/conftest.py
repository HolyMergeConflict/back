import uuid
from sqlalchemy import select
from unittest.mock import patch, MagicMock

import pytest
from httpx import AsyncClient
from httpx import ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.database import get_db
from app.enums.user_role import UserRoleEnum
from app.models.base_db_models import Base
from app.main import app
from app.models.user_table import User
from app.utils.password_utils import PasswordUtils

DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="session")
async def async_engine():
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
async def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture
async def registered_user_and_token(client):
    suffix = uuid.uuid4().hex[:8]
    user_data = {
        "username": f"testuser_{suffix}",
        "email": f"test_{suffix}@example.com",
        "password": "securepassword",
        "role": "student"
    }

    res = await client.post("/auth/register", json=user_data)
    assert res.status_code == 201

    res = await client.post("/auth/login", json={
        "username": user_data["username"],
        "password": user_data["password"]
    })
    assert res.status_code == 200
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    return user_data, token, headers


@pytest.fixture(scope="session", autouse=True)
async def seed_initial_admin(async_engine):
    async_session = async_sessionmaker(bind=async_engine, expire_on_commit=False)

    from app import database
    database.get_db = lambda: async_session()

    async with async_session() as db:
        admin_exists = await db.execute(
            select(User).where(User.username == "admin")
        )
        if admin_exists.scalar_one_or_none():
            return

        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=PasswordUtils.get_password_hash("adminpass"),
            role=UserRoleEnum.ADMIN
        )
        db.add(admin)
        await db.commit()


@pytest.fixture
async def admin_user_and_token(client):
    login_data = {
        "username": "admin",
        "password": "adminpass"
    }
    res = await client.post("/auth/login", json=login_data)
    assert res.status_code == 200
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    return login_data, token, headers


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