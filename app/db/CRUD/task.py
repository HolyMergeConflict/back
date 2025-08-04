from sqlalchemy.ext.asyncio import AsyncSession

from app.db.CRUD.CRUD_base import CRUDBase
from app.models.task_table import Task

class TaskCRUD(CRUDBase[Task]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Task)

    async def get_tasks_by_user(self, user_id: int) -> list[Task]:
        return await self.get_all(creator_id=user_id)

    async def get_task_by_id(self, task_id: int) -> Task | None:
        return await self.get_one(id=task_id)

    async def get_task_by_subject(self, subject: str) -> list[Task]:
        return await self.get_all(subject=subject)

    async def delete_task_by_id(self, task_id: int) -> None:
        await self.delete_by_filter(id=task_id)