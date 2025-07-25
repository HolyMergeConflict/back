from fastapi import APIRouter, HTTPException, Depends
from app.schemas.user import UserCreate, UserPublic, UserLogin
from passlib.hash import bcrypt
from app.auth.jwt import create_access_token
from app.services.user_service import get_user_by_username, create_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserPublic)
async def register(data: UserCreate):
    if await get_user_by_username(data.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed = bcrypt.hash(data.password)
    user = await create_user(data.username, data.email, hashed, data.role)
    return UserPublic(id=user.id, username=user.username, email=user.email)

@router.post("/login")
async def login(data: UserLogin):
    user = await get_user_by_username(data.username)
    if not user or not bcrypt.verify(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token({"sub": user.id})
    return {"access_token": token, "token_type": "bearer"}