from datetime import datetime

from sqlalchemy import Integer, Column, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship

from app.enums.task_solution_status import TaskSolutionStatusEnum
from app.models.base_db_models import Base


class TaskHistory(Base):
    __tablename__ = 'task_history'

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    task_id = Column(Integer, ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)

    status = Column(Enum(TaskSolutionStatusEnum), nullable=False)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)

    user = relationship('User', back_populates='task_history')
    task = relationship('Task', back_populates='task_history')