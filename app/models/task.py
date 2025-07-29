from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Task(BaseModel):
   __tablename__ = 'tasks'

   id = Column(Integer, primary_key=True, index=True)
   title = Column(String, nullable=False)
   description = Column(Text, nullable=False)
   subject = Column(String, nullable=False)

   creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)

   creator = relationship('User', back_populates='tasks')