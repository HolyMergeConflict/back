from datetime import datetime
from typing import override

from sqlalchemy.orm import joinedload

from app.db.CRUD.CRUD_base import CRUDBase
from app.models.task_history_table import TaskHistory


class TaskHistoryCRUD(CRUDBase[TaskHistory]):
    def __init__(self, db):
        super().__init__(db, TaskHistory)


    def get_by_user_and_task(self, user_id: int, task_id: int) -> list[TaskHistory]:
        return self.get_all(user_id=user_id, task_id=task_id)


    def get_in_time_range(self, user_id: int, start_time: datetime, end_time: datetime) -> list[TaskHistory]:
        return self.get_all(self.model.timestamp >= start_time, self.model.timestamp <= end_time, user_id=user_id)


    def get_latest_attempt(self, user_id: int, task_id: int) -> TaskHistory | None:
        return (self.db
                .query(self.model)
                .filter_by(user_id=user_id, task_id=task_id)
                .order_by(self.model.timestamp.desc())
                .first()
                )

    @override
    def create(self, obj: TaskHistory) -> TaskHistory:
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)


        return self.db.query(self.model).options(
            joinedload(self.model.user),
            joinedload(self.model.task)
        ).filter(self.model.id == obj.id).first()