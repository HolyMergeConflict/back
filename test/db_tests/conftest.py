import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

import pytest
from app.db.CRUD.task import TaskCRUD
from app.db.CRUD.task_history import TaskHistoryCRUD
from app.db.CRUD.user import UserCRUD
from app.models.base_db_models import Base

DATABASE_URL = 'sqlite+aiosqlite:///:memory:'

@pytest.fixture(scope='session')
def event_loop():
    import asyncio
    return asyncio.get_event_loop()

@pytest_asyncio.fixture(scope='function', autouse=True)
async def db_session():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        yield session

    await engine.dispose()

@pytest_asyncio.fixture
async def user_crud(db_session) -> UserCRUD:
    return UserCRUD(db_session)

@pytest_asyncio.fixture
async def task_crud(db_session) -> TaskCRUD:
    return TaskCRUD(db_session)

@pytest_asyncio.fixture
async def task_history_crud(db_session) -> TaskHistoryCRUD:
    return TaskHistoryCRUD(db_session)