from sqlalchemy.ext.asyncio import AsyncSession

from app.db.CRUD.user import UserCRUD
from app.enums.user_role import UserRoleEnum
from app.exceptions.user_exception import EmailAlreadyRegistered, UsernameAlreadyTaken, UserNotFound, \
    CannotDemoteSelf, PermissionDeniedUser
from app.logger import setup_logger
from app.models.user_table import User
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, db: AsyncSession):
        self.user_crud = UserCRUD(db)
        self.logger = setup_logger(__name__)


    async def create_user(self, user_data: UserCreate, creator: User = None) -> User:
        role = user_data.role or UserRoleEnum.STUDENT
        self.logger.info(f'Creating user with role: {role}')

        self._validate_role_assignment(role, creator)

        if await  self.user_crud.get_user_by_email(user_data.email):
            self.logger.exception(f'User with email {user_data['email']} already exists',)
            raise EmailAlreadyRegistered()

        if await self.user_crud.get_user_by_username(user_data.email):
            self.logger.exception(f'User with username {user_data['username']} already exists')
            raise UsernameAlreadyTaken()

        user = User(**user_data.model_dump(exclude_unset=True))
        created_user = await self.user_crud.create(user)
        self.logger.info(f'User created successfully with id: {created_user.id}')

        return created_user


    async def update_user_role(self, user_id: int, new_role: UserRoleEnum, admin: User) -> User:
        self.logger.info(f'Updating user role for user with id: {user_id}')
        if not self._is_admin(admin):
            self.logger.exception('Only admins can update user roles')
            raise PermissionDeniedUser()

        user = await self.user_crud.get_one(id=user_id)
        if not user:
            self.logger.exception('User not found')
            raise UserNotFound()

        self._validate_role_assignment(new_role, admin)

        updated_user = await self.user_crud.update(user, {'role': new_role})
        self.logger.info(f'User role updated successfully for user with id: %s, by admin with id: {admin.id}', )
        return updated_user


    async def update_user(self, user_id: int, user_data: UserUpdate, requesting_user: User) -> User:
        if requesting_user.id == user_id:
            self.logger.info(f'Updating user with id: {user_id}')
            return await self.user_crud.update(requesting_user, user_data.model_dump(exclude_unset=True))

        if requesting_user.id != user_id:
            if self._is_admin(requesting_user):
                if user := await self.user_crud.get_one(id=user_id):
                    self.logger.info(f'Updating user with id: {user_id}')
                    return await self.user_crud.update(user, user_data.model_dump(exclude_unset=True))
                else:
                    self.logger.exception('User not found')
                    raise UserNotFound()
            else:
                self.logger.exception('Only admins can update user roles')
                raise PermissionDeniedUser()


    async def promote_to_moderator(self, user_id: int, requesting_user: User) -> User:
        self.logger.info(f'Promoting user to moderator: {user_id}')
        return await self._change_user_role(user_id, UserRoleEnum.MODERATOR, requesting_user)


    async def promote_to_admin(self, user_id: int, admin: User) -> User:
        self.logger.info(f'Promoting user to admin: {user_id}')
        return await self._change_user_role(user_id, UserRoleEnum.ADMIN, admin)


    async def demote_user(self, user_id: int, requesting_user: User, new_role: UserRoleEnum = UserRoleEnum.STUDENT) -> User:
        self.logger.info(f'Demoting user with id: {user_id} to role: {new_role}')
        return await self._change_user_role(user_id, new_role, requesting_user)


    async def get_self_user_by_id(self, user_id: int) -> User:
        self.logger.info(f'Getting user by id: {user_id}')
        return await self.user_crud.get_one(id=user_id)


    async def get_user(self, user_id: int, requesting_user: User) -> User:
        self.logger.info('starting get user')
        if user_id == requesting_user.id:
            self.logger.info(f'Getting user by id: {user_id}')
            return requesting_user
        if user_id != requesting_user.id:
            if self._can_view_users(requesting_user):
                self.logger.info(f'Getting user by id: {user_id}')
                if user := await self.user_crud.get_one(id=user_id):
                    self.logger.info(f'User found: {user_id}')
                    return user
                else:
                    self.logger.exception(f'User not found: {user_id}')
                    raise UserNotFound()
            else:
                self.logger.exception(f'Insufficient permissions to view user: {user_id}')
                raise PermissionDeniedUser()


    async def get_users(self, requesting_user: User, **filters) -> list[User]:
        if not self._can_view_users(requesting_user):
            self.logger.exception(f'Insufficient permissions to view users: {requesting_user.id}')
            raise PermissionDeniedUser()
        self.logger.info(f'Getting users by {requesting_user.id}')
        return await self.user_crud.get_all(**filters)


    async def get_users_by_role(self, role: UserRoleEnum, requesting_user: User) -> list[User]:
        self.logger.info(f'Getting users by role: {role}, requesting user: {requesting_user.id}')
        return await self.get_users(requesting_user, role=role)


    async def _change_user_role(self, user_id: int, new_role: UserRoleEnum, requesting_user: User) -> User:
        if not self._is_admin(requesting_user):
            self.logger.exception(f'Only administrators can change user roles, requesting user: {requesting_user.id}')
            raise PermissionDeniedUser()


        user = await self.user_crud.get_one(id=user_id)
        if not user:
            self.logger.exception(f'User not found, id: {user_id}')
            raise UserNotFound()

        if user.id == requesting_user.id and new_role != UserRoleEnum.ADMIN:
            self.logger.exception(f'Administrators cannot demote themselves, requesting user: {requesting_user.id}')
            raise CannotDemoteSelf()

        updated_user = await self.user_crud.update(user, {'role': new_role})
        self.logger.info(f'User role updated successfully for user with id: ${user_id}, by admin with id: {requesting_user.id}')
        return updated_user

    def _validate_role_assignment(self, role: UserRoleEnum, creator: User = None):
        privileged_roles = {UserRoleEnum.ADMIN, UserRoleEnum.MODERATOR}

        if (role in privileged_roles) and not self._is_admin(creator):
            self.logger.exception('Only administrators can assign admin or moderator roles')
            raise PermissionDeniedUser()


    async def delete_user(self, user: User, requesting_user: User) -> None:
        if not self._is_admin(requesting_user):
            self.logger.exception(f'Only administrators can delete users, requesting user: {requesting_user.id}')
            raise PermissionDeniedUser()

        if not user:
            self.logger.exception(f'User not found, id: {user.id}')
            raise UserNotFound()
        self.logger.info(f'Deleting user with id: {user.id}')
        return await self.user_crud.delete(user)


    async def delete_user_by_id(self, user_id: int, requesting_by: User) -> None:
        if user := await self.user_crud.get_one(id=user_id):
            self.logger.info(f'Deleting user with id: {user_id}')
            await self.delete_user(user, requesting_by)
        else:
            self.logger.exception(f'User not found, id: {user_id}')
            raise UserNotFound()


    @staticmethod
    def _is_admin(user: User) -> bool:
        return user and user.role == UserRoleEnum.ADMIN

    @staticmethod
    def _can_view_users(user: User) -> bool:
        return user and user.role in {UserRoleEnum.ADMIN, UserRoleEnum.MODERATOR}