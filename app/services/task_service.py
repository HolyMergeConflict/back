from sqlalchemy.orm import Session

from app.db.CRUD.task import TaskCRUD
from app.enums.task_moderation_status import TaskStatusEnum
from app.enums.user_role import UserRoleEnum
from app.exceptions.base_exception import MissingRequiredParameters
from app.exceptions.task_exception import PermissionDeniedTask, TaskNotPendingModeration, TaskNotFound
from app.models.task_table import Task
from app.models.user_table import User


class TaskService:
    def __init__(self, db: Session):
        self.task_crud = TaskCRUD(db)

    def create_task(self, task_data: dict, creator: User) -> Task:
        needs_moderation = self._needs_moderation(creator)

        task_data['creator_id'] = creator.id
        task_data['status'] = TaskStatusEnum.PENDING if needs_moderation else TaskStatusEnum.APPROVED

        task = Task(**task_data)

        created_task = self.task_crud.create(task)

        return created_task

    def approve_task(self, task_id: int, moderator: User) -> Task:
        if not self._can_moderate(moderator):
            raise PermissionDeniedTask()

        task = self.task_crud.get_task_by_id(task_id)

        if not task:
            raise TaskNotFound()

        if task.status != TaskStatusEnum.PENDING:
            raise TaskNotPendingModeration()

        updated_task = self.task_crud.update(task, {
            'status': TaskStatusEnum.APPROVED
        })

        return updated_task

    def reject_task(self, task_id: int, moderator: User) -> Task:
        if not self._can_moderate(moderator):
            raise PermissionDeniedTask()

        task = self.task_crud.get_task_by_id(task_id)
        if not task:
            raise TaskNotFound()

        if task.status != TaskStatusEnum.PENDING:
            raise TaskNotPendingModeration()

        updated_task = self.task_crud.update(task, {
            'status': TaskStatusEnum.REJECTED,
        })

        return updated_task

    def get_tasks_for_moderation(self, moderator: User) -> list[Task]:
        if not self._can_moderate(moderator):
            raise PermissionDeniedTask()

        return self.task_crud.get_all(status=TaskStatusEnum.PENDING)

    def delete_task(self, task_id: int, moderator: User) -> None:
        if not self._can_moderate(moderator):
            raise PermissionDeniedTask()

        return self.task_crud.delete_task_by_id(task_id)

    def get_task_by_id(self, task_id: int) -> Task:
        task = self.task_crud.get_task_by_id(task_id)
        if not task:
            raise TaskNotFound()
        return task

    def get_task_by_subject(self, subject: str) -> list[Task]:
        if subject:
            return self.task_crud.get_task_by_subject(subject)
        else:
            raise MissingRequiredParameters('subject is required')

    def get_approved_tasks(self, **filters) -> list[Task]:
        return self.task_crud.get_all(status=TaskStatusEnum.APPROVED, **filters)

    def get_approved_task_by_creator(self, creator: User) -> list[Task]:
        return self.get_approved_tasks(creator_id=creator.id)

    @staticmethod
    def _needs_moderation(user: User) -> bool:
        user_roles = {role.value for role in user.roles}

        privileged_roles = {UserRoleEnum.ADMIN, UserRoleEnum.MODERATOR}
        return not bool(user_roles & privileged_roles)

    @staticmethod
    def _can_moderate(user: User) -> bool:
        user_roles = {role.value for role in user.roles}
        moderator_roles = {UserRoleEnum.ADMIN, UserRoleEnum.MODERATOR}
        return bool(user_roles & moderator_roles)