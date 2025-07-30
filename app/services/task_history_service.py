from datetime import datetime

from sqlalchemy.orm import Session

from app.db.CRUD.task_history import TaskHistoryCRUD
from app.enums.task_moderation_status import TaskStatusEnum
from app.models.task import Task
from app.models.task_history import TaskHistory
from app.models.user import User


class TaskHistoryService:
    def __init__(self, db: Session):
        self.crud = TaskHistoryCRUD(db)

    def log_attempt(self, user: User, task: Task, status: TaskStatusEnum) -> TaskHistory:
        history = TaskHistory(
            user_id=user.id,
            task_id=task.id,
            status=status,
            timestamp=datetime.now()
        )

        return self.crud.create(history)

    def get_user_history(self, user: User) -> list[TaskHistory]:
        return self.crud.get_all(user_id=user.id)

    def get_task_history_for_user(self, user: User, task: Task) -> list[TaskHistory]:
        return self.crud.get_by_user_and_task(user_id=user.id, task_id=task.id)

    def get_latest_result(self, user: User, task: Task) -> TaskHistory | None:
        return self.crud.get_latest_attempt(user_id=user.id, task_id=task.id)