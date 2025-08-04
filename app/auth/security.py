from fastapi import HTTPException, status, Request

from app.models.user_table import User


def get_current_user(request: Request) -> User:
    user = getattr(request.state, 'user', None)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='not authenticated',
        )

    return user
