from datetime import datetime
from typing import override

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db.CRUD.CRUD_base import CRUDBase
from app.models.task_history_table import TaskHistory


class TaskHistoryCRUD(CRUDBase[TaskHistory]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, TaskHistory)


    async def get_by_user_and_task(self, user_id: int, task_id: int) -> list[TaskHistory]:
        return await self.get_all(user_id=user_id, task_id=task_id)


    async def get_in_time_range(self, user_id: int, start_time: datetime, end_time: datetime) -> list[TaskHistory]:
        return await self.get_all(
            self.model.timestamp >= start_time,
            self.model.timestamp <= end_time,
            user_id=user_id
        )

    async def get_latest_attempt(self, user_id: int, task_id: int) -> TaskHistory | None:
        stmt = (
            select(self.model)
            .filter_by(user_id=user_id, task_id=task_id)
            .order_by(self.model.timestamp.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    @override
    async def create(self, obj: TaskHistory) -> TaskHistory:
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)

        stmt = (
            select(self.model)
            .options(
                joinedload(self.model.user),
                joinedload(self.model.task)
            )
            .filter(self.model.id == obj.id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()