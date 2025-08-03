import logging

from sqlalchemy.orm import Session

from app.database import engine, SessionLocal
from app.logger import setup_logger
from app.models.base_db_models import BaseModel
from app.enums.user_role import UserRoleEnum

logger = setup_logger(__name__)

def create_tables() -> None:
    try:
        from app.models import user_table, task_table, task_history_table

        BaseModel.metadata.create_all(bind=engine)
        logger.info('Database tables created successfully')
    except Exception as e:
        logger.error(f'Error creating tables: {e}')
        raise



def init_db() -> None:
    logger.info("Starting database initialization...")

    create_tables()

    db = SessionLocal()


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