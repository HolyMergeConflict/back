from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession as Session
from typing import List

from app.auth.security import get_current_user
from app.database import get_db
from app.enums.task_solution_status import TaskSolutionStatusEnum
from app.models.user_table import User
from app.schemas.task_history import TaskHistoryOut, TaskHistoryCreate
from app.services.task_history_service import TaskHistoryService

router = APIRouter(prefix="/task-history", tags=["Task History"])


@router.post("/", response_model=TaskHistoryOut)
async def log_task_attempt(
        data: TaskHistoryCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return await TaskHistoryService(db).log_attempt(current_user, data)


@router.get("/my", response_model=List[TaskHistoryOut])
async def get_my_history(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return await TaskHistoryService(db).get_user_history(current_user, current_user.id)


@router.get("/my/by-status", response_model=List[TaskHistoryOut])
async def get_my_history_by_status(
        status: TaskSolutionStatusEnum = Query(...),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return await TaskHistoryService(db).get_user_history_by_status(current_user, status)


@router.get("/my/task/{task_id}", response_model=List[TaskHistoryOut])
async def get_my_history_for_task(
        task_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return await TaskHistoryService(db).get_task_history_for_user(current_user, task_id)


@router.get("/my/range", response_model=List[TaskHistoryOut])
async def get_my_history_in_range(
        start: datetime,
        end: datetime,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return await TaskHistoryService(db).get_task_history_in_period(current_user, start, end)


@router.get("/my/task/{task_id}/latest", response_model=TaskHistoryOut | None)
async def get_my_latest_attempt(
        task_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return await TaskHistoryService(db).get_latest_result(current_user, task_id)
