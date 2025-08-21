from pydantic import BaseModel

from app.enums.task_moderation_status import TaskStatusEnum


class TaskBase(BaseModel):
    subject: str
    problem: str
    solution: str
    answer: str
    difficulty: int
    creator_id: int


class TaskCreate(BaseModel):
    subject: str
    problem: str
    solution: str
    answer: str
    difficulty: int

class TaskUpdate(TaskBase):
    subject: str | None = None,
    problem: str | None = None,
    solution: str | None = None,
    answer: str | None = None,
    difficulty: int | None = None
    creator_id: int | None = None


class TaskOut(TaskBase):
    id: int
    status: TaskStatusEnum

    class Config:
        orm_mode = True