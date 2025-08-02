from typing import List, Optional

from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from app.auth.security import get_current_user
from app.database import get_db
from app.enums.task_moderation_status import TaskStatusEnum
from app.models.user_table import User
from app.schemas.task import TaskOut, TaskCreate, TaskBase, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskBase, status_code=status.HTTP_201_CREATED)
def create_task(
        task_data: TaskCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    task_service = TaskService(db)
    return task_service.create_task(task_data.model_dump(), current_user)

@router.get("/", response_model=List[TaskOut])
def get_tasks(
        task_status: Optional[TaskStatusEnum] = None,
        creator_id: Optional[int] = None,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        **filters: dict
):
    task_service = TaskService(db)
    return task_service.get_tasks_by_filters(current_user, status=task_status, creator_id=creator_id, **filters)

@router.get("/my_tasks", response_model=List[TaskBase])
def get_my_tasks(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    task_service = TaskService(db)
    return task_service.get_own_tasks(current_user)

@router.get("/moderation", response_model=List[TaskBase])
def get_tasks_for_moderation(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    task_service = TaskService(db)
    return task_service.get_tasks_for_moderation(current_user)

@router.get("/{task_id}", response_model=TaskBase)
def get_task(
        task_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    task_service = TaskService(db)
    return task_service.get_task_by_id(current_user, task_id)

@router.put("/{task_id}", response_model=TaskBase)
def update_task(
        task_id: int,
        task_data: TaskUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    task_service = TaskService(db)
    return task_service.update_task(task_id, task_data.model_dump(), current_user)


@router.patch("/{task_id}/approve", response_model=TaskBase)
def approve_task(
        task_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    task_service = TaskService(db)
    return task_service.approve_task(task_id, current_user)

@router.patch("/{task_id}/reject", response_model=TaskBase)
def reject_task(
        task_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    task_service = TaskService(db)
    return task_service.reject_task(task_id, current_user)

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
        task_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    task_service = TaskService(db)
    return task_service.delete_task(task_id, current_user)