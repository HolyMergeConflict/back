import logging
import os

from sqlalchemy.orm import Session

from app.database import engine, async_session
from app.db.CRUD.user import UserCRUD
from app.logger import setup_logger
from app.models.base_db_models import BaseModel
from app.enums.user_role import UserRoleEnum
from app.models.user_table import User
from app.utils.password_utils import PasswordUtils

logger = setup_logger(__name__)

async def async_create_tables() -> None:
    try:
        from app.models import user_table, task_table, task_history_table

        async with engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.create_all)
        logger.info('Database tables created successfully')
    except Exception as e:
        logger.error(f'Error creating tables: {e}')
        raise
    

ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

async def create_admin():
    async with async_session() as session:
        crud = UserCRUD(session)

        existing = await crud.get_one(username=ADMIN_USERNAME) or await crud.get_one(email=ADMIN_EMAIL)
        if existing:
            logger.info('[seed] admin already exists, skip')
            return

        hashed = PasswordUtils.get_password_hash(ADMIN_PASSWORD)

        user = User(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            hashed_password=hashed,
            role=UserRoleEnum.ADMIN
        )
        await crud.create(user)
        logger.info(f"[seed] Admin created: {user.username} (id={user.id})")


async def init_db() -> None:
    logger.info("Starting database initialization...")
    await async_create_tables()
    await create_admin()


def reset_database() -> None:
    logger.warning("Resetting database - all data will be lost!")

    try:
        BaseModel.metadata.drop_all(bind=engine)
        logger.info("All tables dropped")

        init_db()
        logger.info("Database reset completed")

    except Exception as e:
        logger.error(f"Database reset failed: {e}")
        raise

if __name__ == "__main__":
    init_db()