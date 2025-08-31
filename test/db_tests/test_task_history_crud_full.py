import pytest
from datetime import datetime, timedelta
from app.models.task_history_table import TaskHistory

@pytest.mark.asyncio
async def test_create_task_history(task_history_crud):
    history = TaskHistory(user_id=1, task_id=2, timestamp=datetime.utcnow(), answer="1234567890", score=100.0, status="RIGHT_SOLUTION", feedback="Good job!")
    created = await task_history_crud.create(history)
    assert created.id is not None

@pytest.mark.asyncio
async def test_get_by_user_and_task(task_history_crud):
    await task_history_crud.create(TaskHistory(user_id=5, task_id=7, answer="1234567890", score=100.0, status="RIGHT_SOLUTION", feedback="Good job!"))
    result = await task_history_crud.get_by_user_and_task(user_id=5, task_id=7)
    assert result
    assert result[0].task_id == 7

@pytest.mark.asyncio
async def test_get_in_time_range(task_history_crud):
    now = datetime.utcnow()
    await task_history_crud.create(TaskHistory(user_id=10, task_id=3, answer='1234', score=100.0, status="RIGHT_SOLUTION", feedback="Good job!", timestamp=now - timedelta(days=1)))
    await task_history_crud.create(TaskHistory(user_id=10, task_id=3, answer='1234', score=100.0, status="RIGHT_SOLUTION", feedback="Good job!",  timestamp=now))
    results = await task_history_crud.get_in_time_range(user_id=10, start_time=now - timedelta(days=2), end_time=now + timedelta(seconds=1))
    assert len(results) >= 2

@pytest.mark.asyncio
async def test_get_latest_attempt(task_history_crud):
    now = datetime.utcnow()
    await task_history_crud.create(TaskHistory(user_id=20, task_id=9, answer='1234', score=100.0, status="RIGHT_SOLUTION", feedback="Good job!", timestamp=now - timedelta(days=1)))
    latest = await task_history_crud.create(TaskHistory(user_id=20, task_id=9, answer='1234', score=100.0, status="RIGHT_SOLUTION", feedback="GJ", timestamp=now))
    result = await task_history_crud.get_latest_attempt(user_id=20, task_id=9)
    assert result.id == latest.id
