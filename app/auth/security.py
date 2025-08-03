from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user_table import User
from app.services.auth_service import AuthService
from app.utils.redis_client import redis_client

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

security = HTTPBearer()

def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
):
    token = credentials.credentials


    if redis_client.get(f'blacklist:{token}') == 'true':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is blacklisted"
        )

    username = AuthService.verify_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user
