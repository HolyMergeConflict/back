from app.db.CRUD.CRUD_base import CRUDBase
from app.models.user_table import User


class UserCRUD(CRUDBase[User]):
    def __init__(self, db):
        super().__init__(db, User)

    def get_user_by_email(self, email: str) -> User:
        return self.get_one(email=email)

    def get_user_by_username(self, username: str) -> User:
        return self.get_one(username=username)