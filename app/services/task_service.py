from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.CRUD.task import create_task, get_task, update_task, delete_task
from app.models.task import Task


def create_user_task(db: Session, task_data: dict, creator_id: int) -> Task:
    task = Task(**task_data, creator_id=creator_id)
    return create_task(db, task)

def get_task_for_user(db: Session, task_id: int) -> Task:
    task = get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

def update_user_task(db: Session, task_id: int, data: dict) -> Task:
    task = get_task_for_user(db, task_id)
    return update_task(db, task, data)

def delete_user_task(db: Session, task_id: int) -> None:
    task = get_task_for_user(db, task_id)
    delete_task(db, task)