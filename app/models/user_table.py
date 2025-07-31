from sqlalchemy import Table, Column, Integer, ForeignKey, String, Boolean, DateTime, func, Enum
from sqlalchemy.orm import relationship

from app.enums.user_role import UserRoleEnum
from app.models.base_db_models import BaseModel, Base

user_role = Table(
    'user_role',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Enum(UserRoleEnum), ForeignKey('role.id'), primary_key=True)
)

class Role(Base):
    __tablename__ = 'role'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)

    users = relationship('User', secondary=user_role, back_populates='role')

class User(BaseModel):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    task_history = relationship('TaskHistory', back_populates='user', cascade='all, delete')

    role = relationship('Role', secondary=user_role, back_populates='users')
    tasks = relationship('Task', back_populates='creator', cascade='all, delete')
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())