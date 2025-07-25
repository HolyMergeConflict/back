from pydantic import BaseModel

class TaskBase(BaseModel):
    text: str
    subject: str
    difficulty: int

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: int

    class Config:
        orm_mode = True