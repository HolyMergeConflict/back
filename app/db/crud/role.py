from typing import Optional, List, cast
from sqlalchemy.orm import Session

from app.db.crud.base import CRUDBase
from app.models.user import Role
from app.models.user_role import UserRoleEnum


class CRUDRole(CRUDBase[Role]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Role]:
        """Получить роль по названию"""
        return db.query(Role).filter(Role.name == name).first()

    def get_roles_with_users_count(self, db: Session) -> List[dict]:
        """Получить роли с количеством пользователей"""
        from sqlalchemy import func
        from app.models.user import user_roles

        result = (
            db.query(
                Role.id,
                Role.name,
                Role.description,
                func.count(user_roles.c.user_id).label('users_count')
            )
            .outerjoin(user_roles, Role.id == user_roles.c.role_id)
            .group_by(Role.id)
            .all()
        )

        return [
            {
                "id": row.id,
                "name": row.name,
                "description": row.description,
                "users_count": row.users_count
            }
            for row in result
        ]

    def get_users_in_role(self, db: Session, *, role_id: int, skip: int = 0, limit: int = 100):
        """Получить пользователей в определенной роли"""
        from app.models.user import User

        role = self.get(db, id=role_id)
        if not role:
            return []

        return role.users[skip:skip + limit]

    def role_exists(self, db: Session, *, name: str) -> bool:
        """Проверить существование роли по имени"""
        return self.get_by_name(db, name=name) is not None

    def delete_role_if_no_users(self, db: Session, *, role_id: int) -> bool:
        """Удалить роль, если у неё нет пользователей"""
        role = self.get(db, id=role_id)
        if not role:
            return False

        if len(role.users) > 0:
            raise ValueError(f"Cannot delete role '{role.name}' - it has {len(role.users)} users")

        db.delete(role)
        db.commit()
        return True

    def get_system_roles(self, db: Session) -> List[Role]:
        """Получить системные роли (admin, moderator, user)"""

        system_role_names = [role.value for role in UserRoleEnum]
        return cast(
            db.query(Role)
            .filter(Role.name.in_(system_role_names))
            .all(), List[Role]
        )

    def get_custom_roles(self, db: Session) -> List[Role]:
        """Получить пользовательские роли (не системные)"""

        system_role_names = [role.value for role in UserRoleEnum]
        return cast(
            db.query(Role)
            .filter(~Role.name.in_(system_role_names))
            .all(), List[Role]
        )

role = CRUDRole(Role)