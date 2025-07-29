import logging

from sqlalchemy.orm import Session

from app.database import engine, SessionLocal
from app.models.base import BaseModel
from app.models.user import Role
from app.models.user_role import UserRoleEnum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables() -> None:
    try:
        from app.models import user, task

        BaseModel.metadata.create_all(bind=engine)
        logger.info('Database tables created successfully')
    except Exception as e:
        logger.error(f'Error creating tables: {e}')
        raise

def init_roles(db: Session) -> list:
    roles_data = [
        {
           'name': UserRoleEnum.ADMIN.value,
            'description': 'Admin role'
        },
        {
            'name': UserRoleEnum.MODERATOR.value,
            'description': 'Moderator role'
        },
        {
            'name': UserRoleEnum.STUDENT.value,
            'description': 'Student role'
        },
        {
            'name': UserRoleEnum.TEACHER.value,
            'description': 'Teacher role'
        }
    ]

    created_roles = []

    for role_data in roles_data:
        existing_role = db.query(Role).filter(Role.name == role_data['name']).first()
        if not existing_role:
            role = Role(**role_data)
            db.add(role)
            created_roles.append(role_data['name'])
            logger.info(f'Created role: {role_data["name"]}')
        else:
            logger.info(f'Role {role_data["name"]} already exists. Skipping creation.')

    if created_roles:
        db.commit()
        logger.info(f'Successfully created {len(created_roles)} roles')

    return created_roles

def init_db() -> None:
    logger.info("Starting database initialization...")

    create_tables()

    db = SessionLocal()
    try:
        init_roles(db)

        logger.info("Database initialization completed successfully")

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

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