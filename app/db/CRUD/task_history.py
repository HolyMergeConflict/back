from app.db.CRUD.CRUD_base import CRUDBase
from app.models.task_history import TaskHistory


class TaskHistoryCRUD(CRUDBase[TaskHistory]):
    def __init__(self, db):
        super().__init__(db, TaskHistory)

    def get_by_user_and_task(self, user_id: int, task_id: int) -> list[TaskHistory]:
        return self.get_all(user_id=user_id, task_id=task_id)

    def get_latest_attempt(self, user_id: int, task_id: int) -> TaskHistory | None:
        return (self.db
                .query(self.model)
                .filter_by(user_id=user_id, task_id=task_id)
                .order_by(self.model.timestamp.desc())
                .first()
                )