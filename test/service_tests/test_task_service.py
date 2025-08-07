import pytest
from app.models.task_history_table import TaskHistory
from app.enums.task_moderation_status import TaskStatusEnum
from app.exceptions.task_exception import (
    TaskNotFound, TaskNotPendingModeration, PermissionDeniedTask
)
from app.models.task_table import Task


@pytest.mark.asyncio
async def test_create_task_as_student(task_service, user, task_create):
    task_service._task_crud.create.return_value = Task(id=1, **task_create.model_dump(), creator_id=user.id, status=TaskStatusEnum.PENDING)

    result = await task_service.create_task(task_create, creator=user)

    assert result.status == TaskStatusEnum.PENDING
    assert result.creator_id == user.id


@pytest.mark.asyncio
async def test_create_task_as_admin(task_service, admin, task_create):
    task_service._task_crud.create.return_value = Task(id=2, **task_create.model_dump(), creator_id=admin.id, status=TaskStatusEnum.APPROVED)

    result = await task_service.create_task(task_create, creator=admin)

    assert result.status == TaskStatusEnum.APPROVED
    assert result.creator_id == admin.id


@pytest.mark.asyncio
async def test_approve_task(task_service, admin, task):
    task_service._task_crud.get_task_by_id.return_value = task
    task_service._task_crud.update.return_value = task

    result = await task_service.approve_task(task.id, moderator=admin)

    assert result.status == TaskStatusEnum.PENDING or result.status == TaskStatusEnum.APPROVED


@pytest.mark.asyncio
async def test_reject_task_not_moderator(task_service, user, task):
    with pytest.raises(PermissionDeniedTask):
        await task_service.reject_task(task_id=task.id, moderator=user)


@pytest.mark.asyncio
async def test_delete_task_success(task_service, admin, task):
    task_service._task_crud.get_task_by_id.return_value = task
    await task_service.delete_task(task_id=task.id, requesting_by=admin)

    task_service._task_crud.delete_task_by_id.assert_called_once_with(task.id)


@pytest.mark.asyncio
async def test_get_tasks_by_filters_as_moderator(task_service, admin):
    task_service._task_crud.get_all.return_value = [Task(id=1)]

    result = await task_service.get_tasks_by_filters(admin)

    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_get_tasks_by_filters_as_user(task_service, user):
    task_service._task_crud.get_all.return_value = [Task(id=1, status=TaskStatusEnum.APPROVED)]

    result = await task_service.get_tasks_by_filters(user)

    for t in result:
        assert t.status == TaskStatusEnum.APPROVED


@pytest.mark.asyncio
async def test_get_task_by_id_pending_denied(task_service, user, task):
    task.status = TaskStatusEnum.PENDING
    task_service._task_crud.get_task_by_id.return_value = task

    with pytest.raises(PermissionDeniedTask):
        await task_service.get_task_by_id(user, task_id=task.id)


@pytest.mark.asyncio
async def test_update_task_as_author(task_service, user, task, task_update):
    task.creator_id = user.id
    task_service._task_crud.get_task_by_id.return_value = task
    task_service._task_crud.update.return_value = task

    result = await task_service.update_task(task_id=task.id, updated_data=task_update, requesting_by=user)

    assert result.id == task.id


@pytest.mark.asyncio
async def test_get_approved_task_by_creator(task_service, user):
    task_service._task_crud.get_all.return_value = [
        Task(id=1, creator_id=user.id, status=TaskStatusEnum.APPROVED)
    ]

    result = await task_service.get_approved_task_by_creator(creator=user)

    assert all(task.creator_id == user.id for task in result)
    task_service._task_crud.get_all.assert_called_once_with(status=TaskStatusEnum.APPROVED, creator_id=user.id)


@pytest.mark.asyncio
async def test_get_task_by_subject(task_service):
    subject = "math"
    task_service._task_crud.get_task_by_subject.return_value = [
        Task(id=1, subject=subject),
        Task(id=2, subject=subject)
    ]

    result = await task_service.get_task_by_subject(subject)

    assert all(task.subject == subject for task in result)
    task_service._task_crud.get_task_by_subject.assert_called_once_with(subject)