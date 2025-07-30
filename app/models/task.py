from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.enums.task_status import TaskStatusEnum
from app.models.base import BaseModel


class Task(BaseModel):
   __tablename__ = 'tasks'

   id = Column(Integer, primary_key=True, index=True)
   title = Column(String, nullable=False)
   description = Column(Text, nullable=False)
   difficulty = Column(Integer, nullable=False)
   subject = Column(String, nullable=False)
   status = Column(Enum(TaskStatusEnum), nullable=False)

   creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)

   creator = relationship('User', back_populates='tasks')