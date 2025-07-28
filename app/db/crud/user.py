from typing import Optional, List
from sqlalchemy.orm import Session

from app.auth.security import get_password_hash, verify_password
from app.db.crud.base import CRUDBase
from app.models.user import User, Role
from app.models.user_role import UserRoleEnum
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            username=obj_in.username,
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            is_active=obj_in.is_active if hasattr(obj_in, 'is_active') else True,
        )

        user_role = db.query(Role).filter(Role.name == UserRoleEnum.STUDENT.value).first()
        if user_role:
            db_obj.roles.append(user_role)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: User, obj_in: UserUpdate) -> User:
        update_data = obj_in.model_dump(exclude_unset=True)

        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password

        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, username: str, password: str) -> Optional[User]:
        user = self.get_by_username(db, username=username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def is_active(user: User) -> bool:
        return user.is_active

    @staticmethod
    def is_superuser(user: User) -> bool:
        return user.has_role(UserRoleEnum.ADMIN.value)

    @staticmethod
    def add_role(db: Session, *, user: User, role_name: str) -> User:
        role = db.query(Role).filter(Role.name == role_name).first()
        if role and role not in user.roles:
            user.roles.append(role)
            db.commit()
            db.refresh(user)
        return user

    @staticmethod
    def remove_role(db: Session, *, user: User, role_name: str) -> User:
        role = db.query(Role).filter(Role.name == role_name).first()
        if role and role in user.roles:
            user.roles.remove(role)
            db.commit()
            db.refresh(user)
        return user

    @staticmethod
    def get_users_by_role(db: Session, *, role_name: str) -> List[User]:
        return (
            db.query(User)
            .join(User.roles)
            .filter(Role.name == role_name)
            .all()
        )

    @staticmethod
    def get_active_users(db: Session, *, skip: int = 0, limit: int = 100) -> List[User]:
        return (
            db.query(User)
            .filter(User.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def deactivate_user(self, db: Session, *, user_id: int) -> Optional[User]:
        user = self.get(db, id=user_id)
        if user:
            user.is_active = False
            db.commit()
            db.refresh(user)
        return user

    def activate_user(self, db: Session, *, user_id: int) -> Optional[User]:
        user = self.get(db, id=user_id)
        if user:
            user.is_active = True
            db.commit()
            db.refresh(user)
        return user

    def search_users(
            self,
            db: Session,
            *,
            query: str,
            skip: int = 0,
            limit: int = 100
    ) -> List[User]:
        return (
            db.query(User)
            .filter(
                (User.username.contains(query)) |
                (User.email.contains(query))
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

user = CRUDUser(User)