from pydantic import BaseModel

from app.enums.task_moderation_status import TaskStatusEnum


class TaskBase(BaseModel):
    title: str
    description: str
    difficulty: int
    subject: str

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    title: str | None = None,
    description: str | None = None,
    difficulty: int | None = None,
    subject: str | None = None,
    status: TaskStatusEnum | None = None,

class TaskOut(TaskBase):
    id: int
    status: TaskStatusEnum

    class Config:
        orm_mode = True