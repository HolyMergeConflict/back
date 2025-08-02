from sqlalchemy.orm import Session

from app.db.CRUD.task import TaskCRUD
from app.enums.task_moderation_status import TaskStatusEnum
from app.enums.user_role import UserRoleEnum
from app.exceptions.base_exception import MissingRequiredParameters
from app.exceptions.task_exception import PermissionDeniedTask, TaskNotPendingModeration, TaskNotFound
from app.logger import setup_logger
from app.models.task_table import Task
from app.models.user_table import User


class TaskService:
    def __init__(self, db: Session):
        self.task_crud = TaskCRUD(db)
        self.logger = setup_logger(__name__)

    def create_task(self, task_data: dict, creator: User) -> Task:
        self.logger.info(f'Creating task by user {creator.id}')
        needs_moderation = self._needs_moderation(creator)

        task_data['creator_id'] = creator.id
        task_data['status'] = TaskStatusEnum.PENDING if needs_moderation else TaskStatusEnum.APPROVED

        task = Task(**task_data)

        created_task = self.task_crud.create(task)
        self.logger.info(f'Task by user {creator.id} created with id {created_task.id}')

        return created_task

    def approve_task(self, task_id: int, moderator: User) -> Task:
        self.logger.info(f'Starting approving task, task_id: {task_id}, moderator: {moderator.id}')
        if not self._can_moderate(moderator):
            self.logger.exception('User is not a moderator. ')
            raise PermissionDeniedTask()

        task = self.task_crud.get_task_by_id(task_id)

        if not task:
            self.logger.exception(f'Task not found, task_id: {task_id}')
            raise TaskNotFound()

        if task.status != TaskStatusEnum.PENDING:
            self.logger.exception(f'Task is not pending moderation, task_id: {task_id}')
            raise TaskNotPendingModeration()

        updated_task = self.task_crud.update(task, {
            'status': TaskStatusEnum.APPROVED
        })
        self.logger.info(f'Task approved, task_id: {task_id}')
        return updated_task

    def reject_task(self, task_id: int, moderator: User) -> Task:
        self.logger.info(f'Starting rejecting task, task_id: {task_id}, moderator: {moderator.id}')
        if not self._can_moderate(moderator):
            self.logger.exception(f'User is not a moderator, user_id: {moderator.id}')
            raise PermissionDeniedTask()

        task = self.task_crud.get_task_by_id(task_id)
        if not task:
            self.logger.exception(f'Task not found, task_id: {task_id}')
            raise TaskNotFound()

        if task.status != TaskStatusEnum.PENDING:
            self.logger.exception(f'Task is not pending moderation, task_id: {task_id}')
            raise TaskNotPendingModeration()

        updated_task = self.task_crud.update(task, {
            'status': TaskStatusEnum.REJECTED,
        })
        self.logger.info(f'Task rejected, task_id: {task_id}, moderator: {moderator.id}')

        return updated_task

    def get_tasks_for_moderation(self, moderator: User) -> list[Task]:
        self.logger.info(f'Getting tasks for moderation, moderator: {moderator.id}')
        if not self._can_moderate(moderator):
            self.logger.exception(f'User is not a moderator, user_id: {moderator.id}')
            raise PermissionDeniedTask()

        self.logger.info(f'Tasks for moderating successfully retrieved, moderator: {moderator.id}')
        return self.task_crud.get_all(status=TaskStatusEnum.PENDING)

    def delete_task(self, task_id: int, moderator: User) -> None:
        self.logger.info(f'Deleting task, task_id: {task_id}, moderator: {moderator.id}')
        if not self._can_moderate(moderator):
            self.logger.exception(f'User is not a moderator, user_id: {moderator.id}')
            raise PermissionDeniedTask()

        self.logger.info(f'Task deleted, task_id: {task_id}, moderator: {moderator.id}')
        return self.task_crud.delete_task_by_id(task_id)

    def get_task_by_id(self, task_id: int) -> Task:
        self.logger.info(f'Getting task by id, task_id: {task_id}')
        task = self.task_crud.get_task_by_id(task_id)
        if not task:
            self.logger.exception(f'Task not found, task_id: {task_id}')
            raise TaskNotFound()
        return task

    def get_task_by_subject(self, subject: str) -> list[Task]:
        self.logger.info(f'Getting task by subject, subject: {subject}')
        if subject:
            return self.task_crud.get_task_by_subject(subject)
        else:
            self.logger.exception(f'Missing required parameters subject')
            raise MissingRequiredParameters('subject is required')

    def get_approved_tasks(self, **filters) -> list[Task]:
        self.logger.info(f'Getting approved tasks, filters: {filters}')
        return self.task_crud.get_all(status=TaskStatusEnum.APPROVED, **filters)

    def get_approved_task_by_creator(self, creator: User) -> list[Task]:
        self.logger.info(f'Getting approved tasks by creator, creator: {creator.id}')
        return self.get_approved_tasks(creator_id=creator.id)

    @staticmethod
    def _needs_moderation(user: User) -> bool:
        return user.role not in {UserRoleEnum.ADMIN, UserRoleEnum.MODERATOR}

    @staticmethod
    def _can_moderate(user: User) -> bool:
        return user.role in {UserRoleEnum.ADMIN, UserRoleEnum.MODERATOR}