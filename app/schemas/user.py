from pydantic import BaseModel, EmailStr
from app.models.user_role import UserRoleEnum


class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRoleEnum | list[UserRoleEnum]

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserPublic(UserBase):
    id: int

    class Config:
        orm_mode = True

class UserUpdate(UserBase):
    password: str