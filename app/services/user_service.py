from sqlalchemy.ext.asyncio import AsyncSession

from app.db.CRUD.user import UserCRUD
from app.enums.user_role import UserRoleEnum
from app.exceptions.user_exception import EmailAlreadyRegistered, UsernameAlreadyTaken, UserNotFound, \
    CannotDemoteSelf
from app.logger import setup_logger
from app.models.user_table import User
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, db: AsyncSession):
        self.user_crud = UserCRUD(db)
        self.logger = setup_logger(__name__)


    async def create_user(self, user_data: UserCreate) -> User:
        role = user_data.role or UserRoleEnum.STUDENT
        self.logger.info(f'Creating user with role: {role}')

        if await  self.user_crud.get_user_by_email(user_data.email):
            self.logger.exception(f'User with email {user_data.email} already exists',)
            raise EmailAlreadyRegistered()

        if await self.user_crud.get_user_by_username(user_data.username):
            self.logger.exception(f'User with username {user_data.username} already exists')
            raise UsernameAlreadyTaken()

        user = User(**user_data.model_dump(exclude_unset=True))
        created_user = await self.user_crud.create(user)
        self.logger.info(f'User created successfully with id: {created_user.id}')

        return created_user


    async def update_user_role(self, user_id: int, new_role: UserRoleEnum, admin: User) -> User:
        self.logger.info(f'Updating user role for user with id: {user_id}')

        user = await self.user_crud.get_one(id=user_id)
        if not user:
            self.logger.exception('User not found')
            raise UserNotFound()

        updated_user = await self.user_crud.update(user, {'role': new_role})
        self.logger.info(f'User role updated successfully for user with id: %s, by admin with id: {admin.id}', )
        return updated_user


    async def update_user(self, user_id: int, user_data: UserUpdate, requesting_user: User) -> User:
        if requesting_user.id == user_id:
            self.logger.info(f'Updating user with id: {user_id}')
            return await self.user_crud.update(requesting_user, user_data.model_dump(exclude_unset=True))

        if requesting_user.id != user_id:
            if user := await self.user_crud.get_one(id=user_id):
                self.logger.info(f'Updating user with id: {user_id}')
                return await self.user_crud.update(user, user_data.model_dump(exclude_unset=True))
            else:
                self.logger.exception('User not found')
                raise UserNotFound()

    async def promote_to_moderator(self, user_id: int) -> User:
        self.logger.info(f'Promoting user to moderator: {user_id}')
        return await self._change_user_role(user_id, UserRoleEnum.MODERATOR)


    async def promote_to_admin(self, user_id: int) -> User:
        self.logger.info(f'Promoting user to admin: {user_id}')
        return await self._change_user_role(user_id, UserRoleEnum.ADMIN)


    async def demote_user(self, user_id: int, new_role: UserRoleEnum = UserRoleEnum.STUDENT) -> User:
        self.logger.info(f'Demoting user with id: {user_id} to role: {new_role}')
        return await self._change_user_role(user_id, new_role)


    async def get_self_user_by_id(self, user_id: int) -> User:
        self.logger.info(f'Getting user by id: {user_id}')
        return await self.user_crud.get_one(id=user_id)


    async def get_user(self, user_id: int, requesting_user: User) -> User:
        self.logger.info('starting get user')
        if user_id == requesting_user.id:
            self.logger.info(f'Getting user by id: {user_id}')
            return requesting_user
        if user_id != requesting_user.id:
            self.logger.info(f'Getting user by id: {user_id}')
            if user := await self.user_crud.get_one(id=user_id):
                self.logger.info(f'User found: {user_id}')
                return user
            else:
                self.logger.exception(f'User not found: {user_id}')
                raise UserNotFound()


    async def get_users(self, requesting_user: User, **filters) -> list[User]:
        self.logger.info(f'Getting users by {requesting_user.id}')
        return await self.user_crud.get_all(**filters)


    async def get_users_by_role(self, role: UserRoleEnum, requesting_user: User) -> list[User]:
        self.logger.info(f'Getting users by role: {role}, requesting user: {requesting_user.id}')
        return await self.get_users(requesting_user, role=role)


    async def _change_user_role(self, user_id: int, new_role: UserRoleEnum) -> User:
        user = await self.user_crud.get_one(id=user_id)
        if not user:
            self.logger.exception(f'User not found, id: {user_id}')
            raise UserNotFound()

        if new_role != UserRoleEnum.ADMIN:
            self.logger.exception(f'Administrators cannot demote themselves')
            raise CannotDemoteSelf()

        updated_user = await self.user_crud.update(user, {'role': new_role})
        self.logger.info(f'User role updated successfully for user with id: ${user_id}')
        return updated_user


    async def delete_user(self, user: User) -> None:
        self.logger.info(f'Deleting user with id: {user.id}')
        return await self.user_crud.delete(user)


    async def delete_user_by_id(self, user_id: int) -> None:
        if user := await self.user_crud.get_one(id=user_id):
            self.logger.info(f'Deleting user with id: {user_id}')
            await self.delete_user(user)
        else:
            self.logger.exception(f'User not found, id: {user_id}')
            raise UserNotFound()
