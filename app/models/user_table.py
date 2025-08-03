from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Enum
from sqlalchemy.orm import relationship

from app.enums.user_role import UserRoleEnum
from app.models.base_db_models import BaseModel

class User(BaseModel):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    task_history = relationship('TaskHistory', back_populates='user', cascade='all, delete')

    role = Column(Enum(UserRoleEnum), default=UserRoleEnum.STUDENT)
    tasks = relationship('Task', back_populates='creator', cascade='all, delete')
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())