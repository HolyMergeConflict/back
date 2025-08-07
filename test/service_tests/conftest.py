import pytest
from unittest.mock import AsyncMock, MagicMock

from app.enums.user_role import UserRoleEnum
from app.models.user_table import User
from app.schemas.user import UserCreate
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
