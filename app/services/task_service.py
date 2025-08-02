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
        self._task_crud = TaskCRUD(db)
        self.logger = setup_logger(__name__)


    def create_task(self, task_data: dict, creator: User) -> Task:
        self.logger.info(f'Creating task by user {creator.id}')
        needs_moderation = self._needs_moderation(creator)

        task_data['creator_id'] = creator.id
        task_data['status'] = TaskStatusEnum.PENDING if needs_moderation else TaskStatusEnum.APPROVED

        task = Task(**task_data)

        created_task = self._task_crud.create(task)
        self.logger.info(f'Task by user {creator.id} created with id {created_task.id}')

        return created_task


    def approve_task(self, task_id: int, moderator: User) -> Task:
        self.logger.info(f'Starting approving task, task_id: {task_id}, moderator: {moderator.id}')
        if not self._can_moderate(moderator):
            self.logger.exception('User is not a moderator. ')
            raise PermissionDeniedTask()

        task = self._task_crud.get_task_by_id(task_id)

        if not task:
            self.logger.exception(f'Task not found, task_id: {task_id}')
            raise TaskNotFound()

        if task.status != TaskStatusEnum.PENDING:
            self.logger.exception(f'Task is not pending moderation, task_id: {task_id}')
            raise TaskNotPendingModeration()

        updated_task = self._task_crud.update(task, {
            'status': TaskStatusEnum.APPROVED
        })
        self.logger.info(f'Task approved, task_id: {task_id}')
        return updated_task


    def reject_task(self, task_id: int, moderator: User) -> Task:
        self.logger.info(f'Starting rejecting task, task_id: {task_id}, moderator: {moderator.id}')
        if not self._can_moderate(moderator):
            self.logger.exception(f'User is not a moderator, user_id: {moderator.id}')
            raise PermissionDeniedTask()

        task = self._task_crud.get_task_by_id(task_id)
        if not task:
            self.logger.exception(f'Task not found, task_id: {task_id}')
            raise TaskNotFound()

        if task.status != TaskStatusEnum.PENDING:
            self.logger.exception(f'Task is not pending moderation, task_id: {task_id}')
            raise TaskNotPendingModeration()

        updated_task = self._task_crud.update(task, {
            'status': TaskStatusEnum.REJECTED,
        })
        self.logger.info(f'Task rejected, task_id: {task_id}, moderator: {moderator.id}')

        return updated_task


    def get_tasks_for_moderation(self, requesting_by: User) -> list[Task]:
        self.logger.info(f'Getting tasks for moderation, moderator: {requesting_by.id}')
        if not self._can_moderate(requesting_by):
            self.logger.exception(f'User is not a moderator, user_id: {requesting_by.id}')
            raise PermissionDeniedTask()

        self.logger.info(f'Tasks for moderating successfully retrieved, moderator: {requesting_by.id}')
        return self._task_crud.get_all(status=TaskStatusEnum.PENDING)


    def delete_task(self, task_id: int, requesting_by: User) -> None:
        self.logger.info(f'Deleting task, task_id: {task_id}, moderator: {requesting_by.id}')
        if not self._can_moderate(requesting_by):
            self.logger.exception(f'User is not a moderator, user_id: {requesting_by.id}')
            raise PermissionDeniedTask()

        self.logger.info(f'Task deleted, task_id: {task_id}, moderator: {requesting_by.id}')
        return self._task_crud.delete_task_by_id(task_id)


    def get_tasks_by_filters(self, requesting_by: User, **filters) -> list[Task]:
        self.logger.info(f'Getting tasks by filters, filters: {filters}, for user: {requesting_by.id}')
        if self._can_moderate(requesting_by):
            self.logger.info('User is a moderator, getting all tasks')
            return self._task_crud.get_all(**filters)
        if not self._can_moderate(requesting_by):
            self.logger.info('User is not a moderator, getting approved tasks')
            return self._task_crud.get_all(**filters, status=TaskStatusEnum.APPROVED)


    def get_task_by_id(self, requesting_by: User, task_id: int) -> Task:
        self.logger.info(f'Getting task by id, task_id: {task_id}')
        task = self._task_crud.get_task_by_id(task_id)
        if not task:
            self.logger.exception(f'Task not found, task_id: {task_id}')
            raise TaskNotFound()

        if (not self._can_moderate(requesting_by)) and task.status == TaskStatusEnum.PENDING:
            self.logger.info('User not is a moderator and task is pending moderation')
            raise PermissionDeniedTask('User is not a moderator and task is pending moderation')
        return task


    def get_own_tasks(self, user: User) -> list[Task]:
        return self._task_crud.get_all(creator_id=user.id)


    def get_task_by_subject(self, subject: str) -> list[Task]:
        self.logger.info(f'Getting task by subject, subject: {subject}')
        if subject:
            return self._task_crud.get_task_by_subject(subject)
        else:
            self.logger.exception(f'Missing required parameters subject')
            raise MissingRequiredParameters('subject is required')


    def get_approved_tasks(self, **filters) -> list[Task]:
        self.logger.info(f'Getting approved tasks, filters: {filters}')
        return self._task_crud.get_all(status=TaskStatusEnum.APPROVED, **filters)


    def get_approved_task_by_creator(self, creator: User) -> list[Task]:
        self.logger.info(f'Getting approved tasks by creator, creator: {creator.id}')
        return self.get_approved_tasks(creator_id=creator.id)


    def update_task(self, task_id: int, updated_data: dict, requesting_by: User) -> Task:
        task = self._task_crud.get_task_by_id(task_id)
        if task.creator_id == requesting_by.id or self._can_moderate(requesting_by):
            return self._task_crud.update(task, updated_data)
        raise PermissionDeniedTask('User is not a moderator and not the creator of the task')



    @staticmethod
    def _needs_moderation(user: User) -> bool:
        return user.role not in {UserRoleEnum.ADMIN, UserRoleEnum.MODERATOR}


    @staticmethod
    def _can_moderate(user: User) -> bool:
        return user.role in {UserRoleEnum.ADMIN, UserRoleEnum.MODERATOR}
