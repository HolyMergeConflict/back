from pydantic import BaseModel, EmailStr
from app.enums.user_role import UserRoleEnum


class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRoleEnum | list[UserRoleEnum]

    class Config:
        from_attributes = True

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserPublic(UserBase):
    id: int


class UserUpdate(UserBase):
    password: str