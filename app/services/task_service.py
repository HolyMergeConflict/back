from typing import List, Optional
from app.schemas.task import TaskCreate, Task

tasks_db = []

task_id_counter = 1

async def get_tasks() -> List[Task]:
    return tasks_db

async def get_task(task_id: int) -> Optional[Task]:
    for task in tasks_db:
        if task.id == task_id:
            return task
    return None

async def create_task(task_create: TaskCreate) -> Task:
    global task_id_counter
    task = Task(
        id=task_id_counter,
        text=task_create.text,
        subject=task_create.subject,
        difficulty=task_create.difficulty
    )
    task_id_counter += 1
    tasks_db.append(task)
    return task
