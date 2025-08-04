from sqlalchemy import select

from app.utils.password_utils import verify_password
from app.db.CRUD.CRUD_base import CRUDBase
from app.models.user_table import User


class UserCRUD(CRUDBase[User]):
    def __init__(self, db):
        super().__init__(db, User)

    async def get_user_by_email(self, email: str) -> User | None:
        return await self.get_one(email=email)

    async def get_user_by_username(self, username: str) -> User | None:
        return await self.get_one(username=username)

    async def authenticate_user(self, username: str, password: str) -> User | None:
        stmt = select(self.model).filter(self.model.username == username)
        result = await self.db.execute(stmt)
        user = result.scalars().first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user