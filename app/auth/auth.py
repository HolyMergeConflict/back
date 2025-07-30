from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.enums.user_role import UserRoleEnum
from app.schemas.user import UserCreate, UserPublic, UserLogin
from passlib.hash import bcrypt
from app.auth.jwt import AuthService
#from app.services.user_service import get_user_by_username, create_user

auth_service = AuthService()

router = APIRouter(prefix="/auth", tags=["auth"])
'''
@router.post("/register", response_model=UserPublic)
async def register(data: UserCreate, db: Session = Depends(get_db)):
    if await get_user_by_username(db, data.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed = bcrypt.hash(data.password)
    user = await create_user(db, data.username, data.email, hashed, data.role)
    return UserPublic(id=user.id,
                      username=user.username,
                      email=user.email,
                      role=[UserRoleEnum(role.name) for role in user.roles]
                      )

@router.post("/login")
async def login(data: UserLogin, db: Session = Depends(get_db)):
    user = await get_user_by_username(db, data.username)
    if not user or not bcrypt.verify(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = auth_service.create_access_token({"sub": user.id})
    return {"access_token": token, "token_type": "bearer"}
'''