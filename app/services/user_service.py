from app.models.user import User
from app.models.user_role import UserRole


async def get_user_by_username(username: str):
    return await User.get_or_none(username=username)

async def create_user(username: str, email: str, hashed_password: str, role: UserRole):
    return await User.create(
        username=username,
        email=email,
        hashed_password=hashed_password,
        role=role,
    )
