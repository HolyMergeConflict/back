import logging

from sqlalchemy.orm import Session

from app.database import engine, async_session
from app.logger import setup_logger
from app.models.base_db_models import BaseModel
from app.enums.user_role import UserRoleEnum

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

async def init_db() -> None:
    logger.info("Starting database initialization...")
    await async_create_tables()


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