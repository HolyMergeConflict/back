from pydantic import BaseModel

from app.enums.task_moderation_status import TaskStatusEnum


class TaskBase(BaseModel):
    title: str
    description: str
    difficulty: int
    subject: str
    status: TaskStatusEnum

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    title: str | None = None,
    description: str | None = None,

class TaskOut(TaskBase):
    id: int

    class Config:
        orm_mode = True