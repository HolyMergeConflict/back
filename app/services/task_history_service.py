from datetime import datetime

from sqlalchemy.orm import Session

from app.db.CRUD.task_history import TaskHistoryCRUD
from app.enums.task_moderation_status import TaskStatusEnum
from app.logger import setup_logger
from app.models.task_table import Task
from app.models.task_history_table import TaskHistory
from app.models.user_table import User


class TaskHistoryService:
    def __init__(self, db: Session):
        self._crud = TaskHistoryCRUD(db)
        self.logger = setup_logger(__name__)

    def log_attempt(self, user: User, task: Task, status: TaskStatusEnum) -> TaskHistory:
        self.logger.info(f'Logging attempt for user {user.username} on task {task.title} with status {status}')
        history = TaskHistory(
            user_id=user.id,
            task_id=task.id,
            status=status,
            timestamp=datetime.now()
        )

        return self._crud.create(history)

    def get_user_history(self, user: User) -> list[TaskHistory]:
        self.logger.info(f'Getting history for user {user.username}')
        return self._crud.get_all(user_id=user.id)

    def get_task_history_for_user(self, user: User, task: Task) -> list[TaskHistory]:
        self.logger.info(f'Getting history for user {user.username} on task {task.title}')
        return self._crud.get_by_user_and_task(user_id=user.id, task_id=task.id)

    def get_latest_result(self, user: User, task: Task) -> TaskHistory | None:
        self.logger.info(f'Getting latest result for user {user.username} on task {task.title}')
        return self._crud.get_latest_attempt(user_id=user.id, task_id=task.id)