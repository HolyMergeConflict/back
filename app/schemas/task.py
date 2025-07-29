from pydantic import BaseModel

class TaskBase(BaseModel):
    title: str
    description: str
    difficulty: int

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    title: str | None = None,
    description: str | None = None,

class TaskOut(TaskBase):
    id: int

    class Config:
        orm_mode = True