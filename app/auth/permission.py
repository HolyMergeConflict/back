from typing import List

from fastapi import Depends, HTTPException, status

from app.auth.security import get_current_user
from app.models.user import User
from app.models.user_role import UserRoleEnum


def require_roles(allowed_roles: List[UserRoleEnum]):
    def role_checker(current_user: User = Depends(get_current_user)):
        user_roles = [role.name for role in current_user.roles]

        if not any(role.value in user_roles for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f'Access denied. Required roles: {[role.value for role in allowed_roles]}.'
            )

        return current_user

    return role_checker

def require_admin(current_user: User = Depends(get_current_user)):
    return require_roles([UserRoleEnum.ADMIN])(current_user)

def require_moderator(current_user: User = Depends(get_current_user)):
    return require_roles([UserRoleEnum.MODERATOR, UserRoleEnum.ADMIN])(current_user)

def require_authenticated_user(current_user: User = Depends(get_current_user)):
    return current_user