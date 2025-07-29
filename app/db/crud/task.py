from sqlalchemy.orm import Session

from app.models.task import Task


def create_task(db: Session, task: Task) -> Task:
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def get_task(db: Session, task_id: int) -> Task | None:
    return db.query(Task).filter(Task.id == task_id).first()

def get_task_by_user(db: Session, user_id: int) -> list[Task]:
    return db.query(Task).filter(Task.creator_id == user_id).all()

def update_task(db: Session, task: Task, data: dict) -> Task:
    for key, value in data.items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task

def delete_task(db: Session, task: Task) -> None:
    db.delete(task)
    db.commit()