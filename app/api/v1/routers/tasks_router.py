from typing import List, Optional

from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.params import Query
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
    return task_service.create_task(task_data.dict(), current_user)

@router.get("/", response_model=List[TaskOut])
def get_tasks(
        status: Optional[TaskStatusEnum] = Query(None, description="Filter by task status"),
        creator_id: Optional[int] = Query(None, description="Filter by creator ID"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    pass

@router.get("/my_tasks", response_model=List[TaskBase])
def get_my_tasks(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    task_service = TaskService(db)
    return task_service.task_crud.get_all(creator_id=current_user.id)

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
    pass

@router.put("/{task_id}", response_model=TaskBase)
def update_task(
        task_id: int,
        task_data: TaskUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
   pass

@router.patch("/{task_id}", response_model=TaskBase)
def partial_update_task(
        task_id: int,
        task_data: TaskUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return update_task(task_id, task_data, db, current_user)

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
    pass