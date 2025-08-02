from app.db.CRUD.task_history import TaskHistoryCRUD
from app.enums.task_solution_status import TaskSolutionStatusEnum
from app.enums.user_role import UserRoleEnum
from app.exceptions.base_exception import PermissionDenied
from app.logger import setup_logger
from app.models.task_history_table import TaskHistory
from app.models.user_table import User


from datetime import datetime
from sqlalchemy.orm import Session

from app.schemas.task_history import TaskHistoryCreate


class TaskHistoryService:
    def __init__(self, db: Session):
        self._crud = TaskHistoryCRUD(db)
        self.logger = setup_logger(__name__)

    def _ensure_own_data(self, user: User, target_user_id: int):
        if user.role != UserRoleEnum.ADMIN and user.id != target_user_id:
            self.logger.warning(f"Access denied: user {user.id} tried to access data of user {target_user_id}")
            raise PermissionDenied("You can only view your own task history")

    def log_attempt(self, user: User, data: TaskHistoryCreate) -> TaskHistory:
        self.logger.info(f'Logging attempt: user={user.username}, task_id={data.task_id}, status={data.status}')

        history = TaskHistory(
            **data.model_dump(),
            user_id=user.id,
            timestamp=datetime.now()
        )
        return self._crud.create(history)

    def get_user_history(self, current_user: User, target_user_id: int) -> list[TaskHistory]:
        self._ensure_own_data(current_user, target_user_id)
        self.logger.info(f'Fetching all history for user_id={target_user_id}')
        return self._crud.get_all(user_id=target_user_id)

    def get_user_history_by_status(self, current_user: User, status: TaskSolutionStatusEnum) -> list[TaskHistory]:
        self.logger.info(f'Fetching history with status={status} for user_id={current_user.id}')
        return self._crud.get_all(user_id=current_user.id, status=status)

    def get_task_history_for_user(self, current_user: User, task_id: int) -> list[TaskHistory]:
        self.logger.info(f'Fetching history for user_id={current_user.id}, task_id={task_id}')
        return self._crud.get_by_user_and_task(user_id=current_user.id, task_id=task_id)

    def get_task_history_in_period(self, current_user: User, start: datetime, end: datetime) -> list[TaskHistory]:
        self.logger.info(f'Fetching history in time range: {start}–{end} for user_id={current_user.id}')
        return self._crud.get_in_time_range(current_user.id, start, end)

    def get_latest_result(self, current_user: User, task_id: int) -> TaskHistory | None:
        self.logger.info(f'Fetching latest result for user_id={current_user.id}, task_id={task_id}')
        return self._crud.get_latest_attempt(user_id=current_user.id, task_id=task_id)
