from app.utils.password_utils import verify_password
from app.db.CRUD.CRUD_base import CRUDBase
from app.models.user_table import User


class UserCRUD(CRUDBase[User]):
    def __init__(self, db):
        super().__init__(db, User)

    def get_user_by_email(self, email: str) -> User:
        return self.get_one(email=email)

    def get_user_by_username(self, username: str) -> User:
        return self.get_one(username=username)

    def authenticate_user(self, username: str, password: str) -> User | None:
        user = self.db.query(User).filter(User.username == username).first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user