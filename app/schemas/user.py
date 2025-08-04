from pydantic import BaseModel, EmailStr
from app.enums.user_role import UserRoleEnum


class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRoleEnum

    class Config:
        from_attributes = True

class UserCreate(UserBase):
    hashed_password: str

class UserLogin(BaseModel):
    username: str
    hashed_password: str

class UserPublic(UserBase):
    id: int

class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    role: UserRoleEnum | None = None
    hashed_password: str | None = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str