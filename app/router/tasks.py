from fastapi import APIRouter, HTTPException
from app.schemas.task import TaskCreate, Task
from app.services.task_service import get_tasks, get_task, create_task

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/", response_model=list[Task])
async def list_tasks():
    return await get_tasks()

@router.get("/{task_id}", response_model=Task)
async def read_task(task_id: int):
    task = await get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/", response_model=Task)
async def create_new_task(task_create: TaskCreate):
    return await create_task(task_create)
