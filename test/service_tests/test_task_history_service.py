import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta

from app.models.task_table import Task
from app.models.user_table import User
from app.enums.task_solution_status import TaskSolutionStatusEnum
from app.enums.user_role import UserRoleEnum
from app.models.task_history_table import TaskHistory
from app.models.user_table import User
from app.schemas.task_history import TaskHistoryCreate
from app.services.task_history_service import TaskHistoryService
from app.exceptions.base_exception import PermissionDenied


@pytest.fixture
def user():
    return User(id=1, username="student", role=UserRoleEnum.STUDENT)


@pytest.fixture
def admin():
    return User(id=999, username="admin", role=UserRoleEnum.ADMIN)


@pytest.fixture
def task_history_data():
    return TaskHistoryCreate(
        task_id=42,
        status=TaskSolutionStatusEnum.RIGHT_SOLUTION,
        answer="42",
        score=100.0,
        feedback="ok"
    )


@pytest.fixture
def crud_mock():
    mock = AsyncMock()
    return mock


@pytest.fixture
def service(crud_mock):
    service = TaskHistoryService(db=MagicMock())
    service._crud = crud_mock
    return service


@pytest.mark.asyncio
async def test_log_attempt(service, user, task_history_data):
    service._crud.create.return_value = TaskHistory(user_id=1, task_id=42)

    result = await service.log_attempt(user, task_history_data)

    assert result.task_id == 42
    service._crud.create.assert_called_once()
    assert result.user_id == 1


@pytest.mark.asyncio
async def test_get_user_history_self(service, user):
    service._crud.get_all.return_value = [TaskHistory(user_id=1)]

    result = await service.get_user_history(user, user.id)

    assert len(result) == 1
    service._crud.get_all.assert_called_once_with(user_id=1)


@pytest.mark.asyncio
async def test_get_user_history_admin(service, admin):
    service._crud.get_all.return_value = [TaskHistory(user_id=123)]

    result = await service.get_user_history(admin, target_user_id=123)

    assert result[0].user_id == 123
    service._crud.get_all.assert_called_once_with(user_id=123)


@pytest.mark.asyncio
async def test_get_user_history_denied(service, user):
    with pytest.raises(PermissionDenied):
        await service.get_user_history(user, target_user_id=999)


@pytest.mark.asyncio
async def test_get_user_history_by_status(service, user):
    service._crud.get_all.return_value = [TaskHistory(user_id=1, status=TaskSolutionStatusEnum.RIGHT_SOLUTION)]

    result = await service.get_user_history_by_status(user, TaskSolutionStatusEnum.RIGHT_SOLUTION)

    assert result[0].status == TaskSolutionStatusEnum.RIGHT_SOLUTION
    service._crud.get_all.assert_called_once_with(user_id=user.id, status=TaskSolutionStatusEnum.RIGHT_SOLUTION)


@pytest.mark.asyncio
async def test_get_task_history_for_user(service, user):
    service._crud.get_by_user_and_task.return_value = [TaskHistory(task_id=123)]

    result = await service.get_task_history_for_user(user, task_id=123)

    assert result[0].task_id == 123
    service._crud.get_by_user_and_task.assert_called_once_with(user_id=user.id, task_id=123)


@pytest.mark.asyncio
async def test_get_task_history_in_period(service, user):
    start = datetime.now() - timedelta(days=1)
    end = datetime.now()

    service._crud.get_in_time_range.return_value = [TaskHistory(id=1)]

    result = await service.get_task_history_in_period(user, start, end)

    service._crud.get_in_time_range.assert_called_once_with(user.id, start, end)
    assert len(result) == 1


@pytest.mark.asyncio
async def test_get_latest_result(service, user):
    latest = TaskHistory(id=99, user_id=1, task_id=77)
    service._crud.get_latest_attempt.return_value = latest

    result = await service.get_latest_result(user, task_id=77)

    assert result.id == 99
    service._crud.get_latest_attempt.assert_called_once_with(user_id=user.id, task_id=77)
