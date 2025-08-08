from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.user import UserCreate, TokenResponse, UserPublic, UserLogin
from app.services.auth_service import AuthService

security = HTTPBearer()

router = APIRouter(prefix="/auth", tags=["Auth"])

async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserPublic)
async def register(user_data: UserCreate, service: AuthService = Depends(get_auth_service)):
    user = await service.register(user_data)
    return UserPublic.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(form_data: UserLogin, service: AuthService = Depends(get_auth_service)):
    return await service.authenticate(form_data.username, form_data.password)

@router.post("/logout")
async def logout(
        credentials: HTTPAuthorizationCredentials = Depends(security),
):
    AuthService.logout(credentials.credentials)
    return {'detail': 'Successfully logged out'}