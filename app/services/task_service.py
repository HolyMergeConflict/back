from sqlalchemy.ext.asyncio import AsyncSession

from app.db.CRUD.task import TaskCRUD
from app.enums.task_moderation_status import TaskStatusEnum
from app.enums.user_role import UserRoleEnum
from app.exceptions.base_exception import MissingRequiredParameters
from app.exceptions.task_exception import PermissionDeniedTask, TaskNotPendingModeration, TaskNotFound
from app.logger import setup_logger
from app.metrics import TASKS_CREATED
from app.models.task_table import Task
from app.models.user_table import User
from app.schemas.task import TaskCreate, TaskUpdate
from app.utils.metrics_utils import count


class TaskService:
    def __init__(self, db: AsyncSession):
        self._task_crud = TaskCRUD(db)
        self.logger = setup_logger(__name__)

    def _task_labels(_self, task_data, *_, **__):
        return {'subject': task_data.subject, "difficulty": task_data.difficulty,}


    @count(TASKS_CREATED, labels=_task_labels)
    async def create_task(self, task_data: TaskCreate, creator: User) -> Task:
        self.logger.info(f'Creating task by user {creator.id}')
        needs_moderation = self._needs_moderation(creator)

        status = TaskStatusEnum.PENDING if needs_moderation else TaskStatusEnum.APPROVED

        task = Task(**task_data.model_dump(exclude_unset=True), creator_id=creator.id, status=status)

        created_task = await self._task_crud.create(task)
        self.logger.info(f'Task by user {creator.id} created with id {created_task.id}')

        return created_task


    async def approve_task(self, task_id: int, moderator: User) -> Task:
        self.logger.info(f'Starting approving task, task_id: {task_id}, moderator: {moderator.id}')
        if not self._can_moderate(moderator):
            self.logger.exception('User is not a moderator. ')
            raise PermissionDeniedTask()

        task = await self._task_crud.get_task_by_id(task_id)

        if not task:
            self.logger.exception(f'Task not found, task_id: {task_id}')
            raise TaskNotFound()

        if task.status != TaskStatusEnum.PENDING:
            self.logger.exception(f'Task is not pending moderation, task_id: {task_id}')
            raise TaskNotPendingModeration()

        updated_task = await self._task_crud.update(task, {
            'status': TaskStatusEnum.APPROVED
        })
        self.logger.info(f'Task approved, task_id: {task_id}')
        return updated_task


    async def reject_task(self, task_id: int, moderator: User) -> Task:
        self.logger.info(f'Starting rejecting task, task_id: {task_id}, moderator: {moderator.id}')
        if not self._can_moderate(moderator):
            self.logger.exception(f'User is not a moderator, user_id: {moderator.id}')
            raise PermissionDeniedTask()

        task = await self._task_crud.get_task_by_id(task_id)
        if not task:
            self.logger.exception(f'Task not found, task_id: {task_id}')
            raise TaskNotFound()

        if task.status != TaskStatusEnum.PENDING:
            self.logger.exception(f'Task is not pending moderation, task_id: {task_id}')
            raise TaskNotPendingModeration()

        updated_task = await self._task_crud.update(task, {
            'status': TaskStatusEnum.REJECTED,
        })
        self.logger.info(f'Task rejected, task_id: {task_id}, moderator: {moderator.id}')

        return updated_task


    async def get_tasks_for_moderation(self, requesting_by: User) -> list[Task]:
        self.logger.info(f'Getting tasks for moderation, moderator: {requesting_by.id}')
        if not self._can_moderate(requesting_by):
            self.logger.exception(f'User is not a moderator, user_id: {requesting_by.id}')
            raise PermissionDeniedTask()

        self.logger.info(f'Tasks for moderating successfully retrieved, moderator: {requesting_by.id}')
        return await self._task_crud.get_all(status=TaskStatusEnum.PENDING)


    async def delete_task(self, task_id: int, requesting_by: User) -> None:
        self.logger.info(f'Deleting task, task_id: {task_id}, moderator: {requesting_by.id}')
        if not self._can_moderate(requesting_by):
            self.logger.exception(f'User is not a moderator, user_id: {requesting_by.id}')
            raise PermissionDeniedTask()

        task = await self._task_crud.get_task_by_id(task_id)
        if not task:
            self.logger.exception(f'Task not found, task_id: {task_id}')
            raise TaskNotFound()

        self.logger.info(f'Task deleted, task_id: {task_id}, moderator: {requesting_by.id}')
        return await self._task_crud.delete_task_by_id(task_id)


    async def get_tasks_by_filters(self, requesting_by: User, **filters):
        filters = {k: v for k, v in filters.items() if v is not None}
        if self._can_moderate(requesting_by):
            return await self._task_crud.get_all(**filters)
        filters.pop('status', None)
        return await self._task_crud.get_all(**filters, status=TaskStatusEnum.APPROVED)


    async def get_task_by_id(self, requesting_by: User, task_id: int) -> Task:
        self.logger.info(f'Getting task by id, task_id: {task_id}')
        task = await self._task_crud.get_task_by_id(task_id)
        if not task:
            self.logger.exception(f'Task not found, task_id: {task_id}')
            raise TaskNotFound()

        if (not self._can_moderate(requesting_by)) and task.status == TaskStatusEnum.PENDING:
            self.logger.info('User not is a moderator and task is pending moderation')
            raise PermissionDeniedTask('User is not a moderator and task is pending moderation')
        return task


    async def get_own_tasks(self, user: User) -> list[Task]:
        return await self._task_crud.get_all(creator_id=user.id)


    async def get_task_by_subject(self, subject: str) -> list[Task]:
        self.logger.info(f'Getting task by subject, subject: {subject}')
        return await self._task_crud.get_task_by_subject(subject)


    async def get_approved_tasks(self, **filters) -> list[Task]:
        self.logger.info(f'Getting approved tasks, filters: {filters}')
        return await self._task_crud.get_all(status=TaskStatusEnum.APPROVED, **filters)


    async def get_approved_task_by_creator(self, creator: User) -> list[Task]:
        self.logger.info(f'Getting approved tasks by creator, creator: {creator.id}')
        return await self.get_approved_tasks(creator_id=creator.id)


    async def update_task(self, task_id: int, updated_data: TaskUpdate, requesting_by: User) -> Task:
        task = await self._task_crud.get_task_by_id(task_id)
        if task.creator_id == requesting_by.id or self._can_moderate(requesting_by):
            return await self._task_crud.update(task, updated_data.model_dump(exclude_unset=True))
        raise PermissionDeniedTask('User is not a moderator and not the creator of the task')


    @staticmethod
    def _needs_moderation(user: User) -> bool:
        return user.role not in {UserRoleEnum.ADMIN, UserRoleEnum.MODERATOR}


    @staticmethod
    def _can_moderate(user: User) -> bool:
        return user.role in {UserRoleEnum.ADMIN, UserRoleEnum.MODERATOR}
