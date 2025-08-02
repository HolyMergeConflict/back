from sqlalchemy.orm import Session

from app.db.CRUD.user import UserCRUD
from app.enums.user_role import UserRoleEnum
from app.exceptions.user_exception import EmailAlreadyRegistered, UsernameAlreadyTaken, UserNotFound, \
    CannotDemoteSelf, PermissionDeniedUser
from app.logger import setup_logger
from app.models.user_table import User

class UserService:
    def __init__(self, db: Session):
        self.user_crud = UserCRUD(db)
        self.logger = setup_logger(__name__)

    def create_user(self, user_data: dict, creator: User = None) -> User:
        role = user_data.get('role', UserRoleEnum.STUDENT)
        self.logger.info(f'Creating user with role: ${user_data['role']}', role)

        self._validate_role_assignment(role, creator)

        if self.user_crud.get_user_by_email(user_data.get('email')):
            self.logger.exception(f'User with email ${user_data['email']} already exists',)
            raise EmailAlreadyRegistered()

        if self.user_crud.get_user_by_username(user_data.get('username')):
            self.logger.exception(f'User with username ${user_data['username']} already exists')
            raise UsernameAlreadyTaken()

        user = User(**user_data)
        created_user = self.user_crud.create(user)
        self.logger.info(f'User created successfully with id: {created_user.id}')

        return created_user

    def update_user_role(self, user_id: int, new_role: UserRoleEnum, admin: User) -> User:
        self.logger.info('Updating user role for user with id: ', user_id)
        if not self._is_admin(admin):
            self.logger.exception('Only admins can update user roles')
            raise PermissionDeniedUser()

        user = self.user_crud.get_one(id=user_id)
        if not user:
            self.logger.exception('User not found')
            raise UserNotFound()

        self._validate_role_assignment(new_role, admin)

        updated_user = self.user_crud.update(user, {'role': new_role})
        self.logger.info('User role updated successfully for user with id: %s, by admin with id: ', admin.id)
        return updated_user

    def update_user(self, user_id: int, user_data: dict, requesting_user: User) -> User:
        if requesting_user.id == user_id:
            self.logger.info('Updating user with id: ', user_id)
            return self.user_crud.update(requesting_user, user_data)

        if requesting_user.id != user_id:
            if self._is_admin(requesting_user):
                if user := self.user_crud.get_one(id=user_id):
                    self.logger.info('Updating user with id: ',user_id)
                    return self.user_crud.update(user, user_data)
                else:
                    self.logger.exception('User not found')
                    raise UserNotFound()
            else:
                self.logger.exception('Only admins can update user roles')
                raise PermissionDeniedUser()

    def promote_to_moderator(self, user_id: int, requesting_user: User) -> User:
        self.logger.info('Promoting user to moderator', user_id)
        return self._change_user_role(user_id, UserRoleEnum.MODERATOR, requesting_user)

    def promote_to_admin(self, user_id: int, admin: User) -> User:
        self.logger.info('Promoting user to admin', user_id)
        return self._change_user_role(user_id, UserRoleEnum.ADMIN, admin)

    def demote_user(self, user_id: int, requesting_user: User, new_role: UserRoleEnum = UserRoleEnum.STUDENT) -> User:
        self.logger.info(f'Demoting user with id: {user_id} to role: {new_role}')
        return self._change_user_role(user_id, new_role, requesting_user)

    def get_self_user_by_id(self, user_id: int) -> User:
        self.logger.info('Getting user by id: ', user_id)
        return self.user_crud.get_one(id=user_id)

    def get_user(self, user_id: int, requesting_user: User) -> User:
        self.logger.info('starting get user')
        if user_id == requesting_user.id:
            self.logger.info('Getting user by id: ', user_id,)
            return requesting_user
        if user_id != requesting_user.id:
            if self._can_view_users(requesting_user):
                self.logger.info('Getting user by id: ',user_id)
                if self.user_crud.get_one(id=user_id):
                    self.logger.info('User found', user_id)
                    return self.user_crud.get_one(id=user_id)
                else:
                    self.logger.exception('User not found',user_id)
                    raise UserNotFound()
            else:
                self.logger.exception('Insufficient permissions to view user', user_id)
                raise PermissionDeniedUser()

    def get_users(self, requesting_user: User, **filters) -> list[User]:
        if not self._can_view_users(requesting_user):
            self.logger.exception('Insufficient permissions to view users',requesting_user.id)
            raise PermissionDeniedUser()
        self.logger.info('Getting users', requesting_user.id)
        return self.user_crud.get_all(**filters)

    def get_users_by_role(self, role: UserRoleEnum, requesting_user: User) -> list[User]:
        self.logger.info('Getting users by role: ', role, requesting_user.id)
        return self.get_users(requesting_user, role=role)

    def _change_user_role(self, user_id: int, new_role: UserRoleEnum, requesting_user: User) -> User:
        if not self._is_admin(requesting_user):
            self.logger.exception('Only administrators can change user roles', requesting_user.id)
            raise PermissionDeniedUser()

        user = self.user_crud.get_one(id=user_id)
        if not user:
            self.logger.exception('User not found', user_id)
            raise UserNotFound()

        if user.id == requesting_user.id and new_role != UserRoleEnum.ADMIN:
            self.logger.exception('Administrators cannot demote themselves', requesting_user.id)
            raise CannotDemoteSelf()

        updated_user = self.user_crud.update(user, {'role': new_role})
        self.logger.info(f'User role updated successfully for user with id: ${user_id}, by admin with id: {requesting_user.id}')
        return updated_user

    def _validate_role_assignment(self, role: UserRoleEnum, creator: User = None):
        privileged_roles = {UserRoleEnum.ADMIN, UserRoleEnum.MODERATOR}

        if (role in privileged_roles) and not self._is_admin(creator):
            self.logger.exception('Only administrators can assign admin or moderator roles')
            raise PermissionDeniedUser()

    def delete_user(self, user: User, admin: User) -> None:
        if not self._is_admin(admin):
            self.logger.exception('Only administrators can delete users', admin.id)
            raise PermissionDeniedUser()

        if not user:
            self.logger.exception('User not found', admin.id)
            raise UserNotFound
        self.logger.info('Deleting user with id: ', user.id)
        return self.user_crud.delete(user)

    def delete_user_by_id(self, user_id: int, admin: User) -> None:
        if user := self.user_crud.get_one(id=user_id):
            self.logger.info('Deleting user with id: ', user.id)
            self.delete_user(user, admin)
        else:
            self.logger.exception('User not found', user_id)
            raise UserNotFound

    @staticmethod
    def _is_admin(user: User) -> bool:
        return user and user.role == UserRoleEnum.ADMIN

    @staticmethod
    def _can_view_users(user: User) -> bool:
        return user and user.role in {UserRoleEnum.ADMIN, UserRoleEnum.MODERATOR}