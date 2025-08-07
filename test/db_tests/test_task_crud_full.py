
import pytest
from app.models.task_table import Task

@pytest.mark.asyncio
async def test_create_task(task_crud):
    task = Task(title='Test Task', description='Test Description', answer='Test Answer', difficulty=1, subject='math', creator_id=1, status='pending')
    created = await task_crud.create(task)
    assert created.id is not None
    assert created.title == 'Test Task'

@pytest.mark.asyncio
async def test_get_task_by_id(task_crud):
    task = Task(title='Find Me', description='Find Me', answer='Find Me', difficulty=1, subject='math', creator_id=1, status='pending')
    created = await task_crud.create(task)
    result = await task_crud.get_task_by_id(created.id)
    assert result is not None
    assert result.title == 'Find Me'

@pytest.mark.asyncio
async def test_get_tasks_by_user(task_crud):
    await task_crud.create(Task(title='User Task 1', description='User Task 1', answer='User Task 1', difficulty=1, subject='math', creator_id=10, status='pending'))
    await task_crud.create(Task(title='User Task 2', description='User Task 2', answer='User Task 2', difficulty=1, subject='math', creator_id=10, status='pending'))
    tasks = await task_crud.get_tasks_by_user(user_id=10)
    assert len(tasks) >= 2

@pytest.mark.asyncio
async def test_delete_task_by_id(task_crud):
    task = Task(title='To Delete', subject='cs', creator_id=3, difficulty=1, status='pending', description='To Delete', answer='To Delete')
    created = await task_crud.create(task)
    await task_crud.delete_task_by_id(created.id)
    result = await task_crud.get_task_by_id(created.id)
    assert result is None
