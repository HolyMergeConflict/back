import pytest
from unittest.mock import AsyncMock, MagicMock

from app.enums.task_moderation_status import TaskStatusEnum
from app.enums.user_role import UserRoleEnum
from app.models.task_table import Task
from app.models.user_table import User
from app.schemas.task import TaskUpdate, TaskCreate
from app.schemas.user import UserCreate
from app.services.auth_service import AuthService
from app.services.task_service import TaskService
from app.services.user_service import UserService


@pytest.fixture
def user() -> User:
    return User(id=1, username="user", email="user@example.com", role=UserRoleEnum.STUDENT)


@pytest.fixture
def admin() -> User:
    return User(id=999, username="admin", email="admin@example.com", role=UserRoleEnum.ADMIN)


@pytest.fixture
def user_data() -> UserCreate:
    return UserCreate(
        username="newuser",
        email="new@example.com",
        hashed_password="securepassword123",
        role=UserRoleEnum.STUDENT
    )


@pytest.fixture
def db_mock():
    return MagicMock()


@pytest.fixture
def user_service(db_mock):
    service = UserService(db=db_mock)
    service.user_crud = AsyncMock()
    return service


@pytest.fixture
def task_create():
    return TaskCreate(
        title="test",
        description="desc",
        answer="42",
        difficulty=1,
        subject="math",
    )

@pytest.fixture
def task_update():
    return TaskUpdate(title="new title")

@pytest.fixture
def task():
    return Task(id=1, creator_id=1, title="t", description="d", answer="42", difficulty=1,
                subject="math", status=TaskStatusEnum.PENDING)

@pytest.fixture
def task_service(db_mock):
    service = TaskService(db=db_mock)
    service._task_crud = AsyncMock()
    return service


@pytest.fixture
def auth_service(db_mock):
    service = AuthService(db=db_mock)
    service.user_crud = AsyncMock()
    return service

@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    mock = MagicMock()
    mock.exists.return_value = False
    mock.expire.return_value = None
    monkeypatch.setattr("app.services.auth_service.redis_client", mock)