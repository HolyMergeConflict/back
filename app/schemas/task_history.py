from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.enums.task_solution_status import TaskSolutionStatusEnum


class TaskHistoryBase(BaseModel):
    status: TaskSolutionStatusEnum
    answer: Optional[str] = None
    score: Optional[float] = None
    feedback: Optional[str] = None
    timestamp: datetime

class TaskHistoryOut(TaskHistoryBase):
    id: int
    user_id: int
    task_id: int

    class Config:
        orm_mode = True

class TaskHistoryUpdate(TaskHistoryBase):
    pass

class TaskHistoryCreate(BaseModel):
    task_id: int
    status: TaskSolutionStatusEnum
    answer: str
    score: float
    feedback: Optional[str] = None