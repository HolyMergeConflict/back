from typing import List

from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from app.auth.security import get_current_user
from app.database import get_db
from app.enums.user_role import UserRoleEnum
from app.models.user_table import User
from app.schemas.user import  UserPublic, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])

@router.get('/', response_model= List[UserPublic])
def get_users(
        db: Session = Depends(get_db),
        role: UserRoleEnum = None,
        current_user: User = Depends(get_current_user)
):
    user_service = UserService(db)
    if role:
        return user_service.get_users_by_role(role, current_user)
    if role is None:
        return user_service.get_users(current_user)

@router.get('/me', response_model=UserPublic)
def get_user_me(
        current_user: User = Depends(get_current_user)
):
    return current_user

@router.get('/{user_id}', response_model=UserPublic)
def get_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    user_service = UserService(db)
    return user_service.get_user(user_id, current_user)

@router.put('/{user_id}', response_model=UserPublic)
def update_user(
        user_id: int,
        user_data: UserUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    user_service = UserService(db)
    return user_service.update_user(user_id, user_data.model_dump(), current_user)

@router.patch('/{user_id}/role', response_model=UserPublic)
def update_user_roles(
        user_id: int,
        new_role: UserRoleEnum,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    user_service = UserService(db)
    return user_service.update_user_role(user_id, new_role, current_user)

@router.patch("/{user_id}/promote/moderator", response_model=UserPublic)
def promote_to_moderator(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    user_service = UserService(db)
    return user_service.promote_to_moderator(user_id, current_user)

@router.patch("/{user_id}/promote/admin", response_model=UserPublic)
def promote_to_admin(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    user_service = UserService(db)
    return user_service.promote_to_admin(user_id, current_user)

@router.patch("/{user_id}/demote", response_model=UserPublic)
def demote_user(
        user_id: int,
        new_role: UserRoleEnum = UserRoleEnum.STUDENT,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    user_service = UserService(db)
    return user_service.demote_user(user_id, current_user, new_role)

@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    user_service = UserService(db)
    user_service.delete_user_by_id(user_id, current_user)