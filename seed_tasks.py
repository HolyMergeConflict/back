import os
import asyncio
import csv
from typing import Optional

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./app.db")
CREATOR_ID = int(os.getenv("CREATOR_ID", "1"))
CSV_PATH = os.getenv("CSV_PATH", "problems.csv")
DEFAULT_STATUS = os.getenv("DEFAULT_STATUS", "PENDING")

from app.models.task_table import Task
from app.enums.task_moderation_status import TaskStatusEnum

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

def to_int_or_none(v: Optional[str]) -> Optional[int]:
    try:
        return int(v) if v not in (None, "",) else None
    except ValueError:
        return None

def status_from_env(name: str) -> TaskStatusEnum:
    try:
        return TaskStatusEnum[name]
    except KeyError:
        return list(TaskStatusEnum)[0]

async def seed():
    status = status_from_env(DEFAULT_STATUS)
    created, skipped, failed = 0, 0, 0

    async with AsyncSessionLocal() as session:
        with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    subject = (row.get("subject") or "").strip()
                    problem = (row.get("problem") or "").strip()
                    solution = (row.get("solution") or "").strip()
                    answer = (row.get("answer") or "").strip()
                    difficulty = to_int_or_none(row.get("difficulty"))

                    if not (subject and problem and solution and answer and isinstance(difficulty, int)):
                        skipped += 1
                        continue

                    exists = await session.execute(
                        Task.__table__.select().where(
                            (Task.problem == problem) & (Task.answer == answer)
                        ).limit(1)
                    )
                    if exists.first():
                        skipped += 1
                        continue

                    task = Task(
                        subject=subject,
                        problem=problem,
                        solution=solution,
                        answer=answer,
                        difficulty=difficulty,
                        status=status,
                        creator_id=CREATOR_ID,
                    )
                    session.add(task)
                    created += 1

                    if created % 500 == 0:
                        await session.flush()
                        await session.commit()
                except Exception as e:
                    raise Exception(f"Ошибка при обработке строки: {row}\nОшибка: {e}") from e

            await session.flush()
            await session.commit()

    print(f"Seed finished. created={created}, skipped={skipped}, failed={failed}")

if __name__ == "__main__":
    asyncio.run(seed())
