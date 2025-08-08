import os

from dotenv import load_dotenv
from jose import jwt, JWTError
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException, status

from app.utils.redis_client import redis_client

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM', 'HS256')

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = None
        auth_header = request.headers.get('Authorization')

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header[7:]

        if token:
            if redis_client.get(f'blacklist:{token}') == b'true':
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='Token is blacklisted',
                )

            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                username = payload.get('sub')
                if not username:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')
                request.state.username = username
            except JWTError:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')

        return await call_next(request)
