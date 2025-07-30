from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.CRUD.user import UserCRUD
from app.enums.user_role import UserRoleEnum
from app.models.user import User

class UserService:
    def __init__(self, db: Session):
        self.user_crud = UserCRUD(db)

    def create_user(self, user_data: dict, creator: User = None) -> User:
        role = user_data.get('role', UserRoleEnum.STUDENT)

        self._validate_role_assignment(role, creator)

        if self.user_crud.get_user_by_email(user_data.get('email')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='User with this email already exists'
            )

        if self.user_crud.get_user_by_username(user_data.get('username')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='User with this username already exists'
            )

        user = User(**user_data)
        created_user = self.user_crud.create(user)

        return created_user

    def update_user_roles(self, user_id: int, new_role: UserRoleEnum, admin: User) -> User:
        if not self._is_admin(admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Only admins can update user roles'
            )

        user = self.user_crud.get_one(id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found'
            )

        self._validate_role_assignment(new_role, admin)

        updated_user = self.user_crud.update(user, {'role': new_role})

        return updated_user

    def promote_to_moderator(self, user_id: int, admin: User) -> User:
        return self._change_user_role(user_id, UserRoleEnum.MODERATOR, admin)

    def promote_to_admin(self, user_id: int, admin: User) -> User:
        return self._change_user_role(user_id, UserRoleEnum.ADMIN, admin)

    def demote_user(self, user_id: int, admin: User, new_role: UserRoleEnum = UserRoleEnum.STUDENT) -> User:
        return self._change_user_role(user_id, new_role, admin)

    def get_users_by_role(self, role: UserRoleEnum, requesting_user: User) -> list[User]:
        if not self._can_view_users(requesting_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view users"
            )
        return self.user_crud.get_all(role=role)

    def _change_user_role(self, user_id: int, new_role: UserRoleEnum, admin: User) -> User:
        if not self._is_admin(admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can change user roles"
            )

        user = self.user_crud.get_one(id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if user.id == admin.id and new_role != UserRoleEnum.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Administrators cannot demote themselves"
            )

        updated_user = self.user_crud.update(user, {'roles': [new_role]})

        return updated_user

    def _validate_role_assignment(self, role: UserRoleEnum, creator: User = None):
        privileged_roles = {UserRoleEnum.ADMIN, UserRoleEnum.MODERATOR}

        if (role in privileged_roles) and not self._is_admin(creator):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can assign admin or moderator roles"
            )

    def delete_user(self, user: User, admin: User) -> None:
        if not self._is_admin(admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can delete users"
            )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return self.user_crud.delete(user)

    @staticmethod
    def _is_admin(user: User) -> bool:
        if not user:
            return False
        user_roles = {role.value for role in user.roles}
        return UserRoleEnum.ADMIN.value in user_roles

    @staticmethod
    def _can_view_users(user: User) -> bool:
        user_roles = {role.value for role in user.roles}
        privileged_roles = {UserRoleEnum.ADMIN.value, UserRoleEnum.MODERATOR.value}
        return bool(user_roles & privileged_roles)