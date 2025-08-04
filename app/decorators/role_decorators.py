from functools import wraps
from fastapi import HTTPException, status

from app.enums.user_role import UserRoleEnum


def require_role(*allowed_roles: UserRoleEnum):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if current_user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='Unauthorized',
                )

            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail='Access forbidden',
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_admin():
    return require_role(UserRoleEnum.ADMIN)

def require_moderator():
    return require_role(UserRoleEnum.MODERATOR, UserRoleEnum.ADMIN)

def require_teacher():
    return require_role(UserRoleEnum.TEACHER, UserRoleEnum.MODERATOR, UserRoleEnum.ADMIN)

def require_admin_or_self():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            user_id = kwargs.get('user_id')

            if current_user is None:
                raise HTTPException(status_code=401, detail="Unauthorized")

            if current_user.role == UserRoleEnum.ADMIN or current_user.id == user_id:
                return await func(*args, **kwargs)

            raise HTTPException(status_code=403, detail="Access denied")

        return wrapper
    return decorator
