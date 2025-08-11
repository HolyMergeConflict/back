import os
from datetime import timedelta, datetime
from typing import Optional

from dotenv import load_dotenv
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.CRUD.user import UserCRUD
from app.exceptions.base_exception import ServiceException
from app.logger import setup_logger
from app.metrics import AUTH_LOGINS
from app.models.user_table import User
from app.schemas.user import UserCreate, TokenResponse
from app.services.user_service import UserService
from app.utils.metrics_utils import count_success_failure
from app.utils.password_utils import PasswordUtils
from app.utils.redis_client import redis_client

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 10))
ALGORITHM = os.getenv('ALGORITHM', 'HS256')

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, db: AsyncSession):
        self.user_crud = UserCRUD(db)
        self.user_service = UserService(db)
        self.logger = setup_logger(__name__)


    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.now() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


    @staticmethod
    def verify_token(token: str) -> str:
        if redis_client.exists(f'access_token:{token}'):
            raise ServiceException('Token revoked', status_code=401)
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            sub = payload.get("sub")
            if sub is None:
                raise JWTError("Missing subject")
            return sub
        except JWTError as e:
            raise ServiceException("Invalid token", status_code=401) from e


    async def register(self, user_data: UserCreate) -> User:
        return await self.user_service.create_user(user_data)

    @count_success_failure(AUTH_LOGINS)
    async def authenticate(self, username: str, password: str) -> TokenResponse:
        self.logger.info('Starting authentication')
        user = await self.user_crud.get_user_by_username(username)
        if not user or not PasswordUtils.verify_password(password, user.hashed_password):
            self.logger.exception(f'Authentication failed for user {username}')
            raise ServiceException("Invalid credentials", status_code=401)

        token = self.create_access_token(data={"sub": user.username})
        self.logger.info('Authentication successful')
        return TokenResponse(access_token=token, token_type="bearer")


    @staticmethod
    def logout(token: str) -> None:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        ttl = int(payload['exp'] - datetime.now().timestamp())
        redis_client.setex(f'access_token:{token}', ttl, 'revoked')
