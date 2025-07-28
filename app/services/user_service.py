from sqlalchemy.orm import Session

from app.models.user import User, Role
from app.models.user_role import UserRoleEnum


async def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()

async def create_user(db: Session,
                      username: str,
                      email: str,
                      hashed_password: str,
                      roles: UserRoleEnum | list[UserRoleEnum]
                      ) -> User:
    if isinstance(roles, UserRoleEnum):
        roles = [roles]

    db_roles = db.query(Role).filter(Role.name.in_([r.value for r in roles])).all()

    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        roles=db_roles
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user
