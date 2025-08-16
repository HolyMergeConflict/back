import asyncio
import os

from app.database import async_session
from app.db.CRUD.user import UserCRUD
from app.enums.user_role import UserRoleEnum
from app.models.user_table import User
from app.utils.password_utils import PasswordUtils

#DEAD CODE

ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

async def main():
    async with async_session() as session:
        crud = UserCRUD(session)

        existing = await crud.get_one(username=ADMIN_USERNAME) or await crud.get_one(email=ADMIN_EMAIL)
        if existing:
            print('[seed] admin already exists, skip')
            return

        hashed = PasswordUtils.get_password_hash(ADMIN_PASSWORD)

        user = User(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            hashed_password=hashed,
            role=UserRoleEnum.ADMIN
        )
        await crud.create(user)
        print(f"[seed] Admin created: {user.username} (id={user.id})")

if __name__ == '__main__':
    asyncio.run(main())