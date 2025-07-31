from app.db.CRUD.CRUD_base import CRUDBase
from app.models.task_table import Task

class TaskCRUD(CRUDBase[Task]):
    def __init__(self, db):
        super().__init__(db, Task)

    def get_tasks_by_user(self, user_id: int) -> list[Task]:
        return self.get_all(creator_id=user_id)

    def get_task_by_id(self, task_id: int) -> Task | None:
        return self.get_one(id=task_id)

    def get_task_by_subject(self, subject: str) -> list[Task]:
        return self.get_all(subject=subject)

    def delete_task_by_id(self, task_id: int) -> None:
        self.delete_by_filter(id=task_id)