import pytest
from app.models.task_table import Task

@pytest.mark.asyncio
async def test_create_task(task_crud):
    task = Task(subject='Math', problem='1', solution='1', answer='1', difficulty=1, status='pending', creator_id = 1)
    created = await task_crud.create(task)
    assert created.id is not None
    assert created.subject == 'Math'

@pytest.mark.asyncio
async def test_get_task_by_id(task_crud):
    task = Task(subject='Math', problem='Find me', solution='Find me', answer='1', difficulty=1, status='pending', creator_id = 1)
    created = await task_crud.create(task)
    result = await task_crud.get_task_by_id(created.id)
    assert result is not None
    assert result.problem == 'Find me'

@pytest.mark.asyncio
async def test_get_tasks_by_user(task_crud):
    await task_crud.create(Task(problem='User Task 1', solution='solution', answer='User Task 1', difficulty=1, subject='math', creator_id=10, status='pending'))
    await task_crud.create(Task(problem='User Task 2', solution='solution', answer='User Task 2', difficulty=1, subject='math', creator_id=10, status='pending'))
    tasks = await task_crud.get_tasks_by_user(user_id=10)
    assert len(tasks) >= 2

@pytest.mark.asyncio
async def test_delete_task_by_id(task_crud):
    task = Task(problem='To Delete', solution='To Delete', subject='cs', creator_id=3, difficulty=1, status='pending', answer='To Delete')
    created = await task_crud.create(task)
    await task_crud.delete_task_by_id(created.id)
    result = await task_crud.get_task_by_id(created.id)
    assert result is None
