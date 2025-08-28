import os
import asyncio
import csv
import re
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models.base_db_models import Base
from app.models.task_history_table import TaskHistory
from app.models.user_table import User

DATABASE_URL = "sqlite+aiosqlite:///app/app.db"
CREATOR_ID = int(os.getenv("CREATOR_ID", "1"))
CSV_PATH = os.getenv("CSV_PATH", "problems.csv")
DEFAULT_STATUS = os.getenv("DEFAULT_STATUS", "PENDING")

from app.models.task_table import Task
from app.enums.task_moderation_status import TaskStatusEnum

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

_ws_re = re.compile(r"\s+")
ANS_RE = re.compile(r"(?:^|\b)(?:ответ|ответ:)\s*[:\-–]?\s*(.+)$", re.IGNORECASE)

def normalize_text(s: Optional[str]) -> str:
    s = (s or "").strip()
    return _ws_re.sub(" ", s)

def to_int_or_default(v: Optional[str], default: int = 1) -> int:
    try:
        if v is None: return default
        v = v.strip()
        return int(v) if v != "" else default
    except Exception:
        return default

def status_from_env(name: str) -> TaskStatusEnum:
    try:
        return TaskStatusEnum[name]
    except KeyError:
        return list(TaskStatusEnum)[0]

async def ensure_schema():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def is_duplicate(session: AsyncSession, problem: str, answer: str, subject: str) -> bool:
    stmt = (
        select(Task.id)
        .where(Task.problem == problem)
        .where(Task.answer == answer)
        .where(Task.subject == subject)
        .limit(1)
    )
    res = await session.execute(stmt)
    return res.first() is not None

def extract_answer(solution: str) -> str | None:
    s = (solution or "").strip()
    if not s:
        return None
    m = ANS_RE.search(s)
    if m:
        return m.group(1).strip()
    if len(s) <= 120 and ("\n" not in s) and (s.count(".") <= 2):
        return s
    return None

async def seed():
    await ensure_schema()

    status = status_from_env(DEFAULT_STATUS)
    created = 0
    skipped_total = 0
    failed = 0

    reasons = {"missing_required": 0, "dup": 0}
    examples = {"missing_required": [], "dup": []}
    fail_examples = []

    async with AsyncSessionLocal() as session:
        with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=1):
                try:
                    subject  = normalize_text(row.get("subject"))
                    problem  = normalize_text(row.get("problem"))
                    solution = normalize_text(row.get("solution"))
                    answer   = normalize_text(row.get("answer"))
                    diff     = to_int_or_default(row.get("difficulty"), default=1)

                    if not answer:
                        extracted = extract_answer(solution)
                        answer = extracted or "(см. решение)"

                    if not subject or not problem or not solution or not answer:
                        skipped_total += 1
                        reasons["missing_required"] += 1
                        if len(examples["missing_required"]) < 3:
                            examples["missing_required"].append(
                                {"row": i, "subject": subject, "problem": problem[:80], "answer": answer}
                            )
                        continue

                    if await is_duplicate(session, problem, answer, subject):
                        skipped_total += 1
                        reasons["dup"] += 1
                        if len(examples["dup"]) < 3:
                            examples["dup"].append(
                                {"row": i, "problem": problem[:80], "answer": answer[:80], "subject": subject}
                            )
                        continue

                    task = Task(
                        subject=subject,
                        problem=problem,
                        solution=solution,
                        answer=answer,
                        difficulty=diff,
                        status=status,
                        creator_id=CREATOR_ID,
                    )
                    session.add(task)
                    created += 1

                    if created % 500 == 0:
                        await session.flush()
                        await session.commit()

                except Exception as e:
                    failed += 1
                    if len(fail_examples) < 5:
                        fail_examples.append({"row": i, "error": str(e), "row_sample": {k: (v or "")[:100] for k, v in row.items()}})
                    continue

            await session.flush()
            await session.commit()

    print(f"Seed finished. created={created}, skipped={skipped_total}, failed={failed}")
    print("Skip breakdown:", reasons)
    if examples["missing_required"]:
        print("Examples for missing_required:")
        for ex in examples["missing_required"]:
            print("  ", ex)
    if examples["dup"]:
        print("Examples for dup:")
        for ex in examples["dup"]:
            print("  ", ex)
    if fail_examples:
        print("Examples for failed (first 5):")
        for ex in fail_examples:
            print("  ", ex)

if __name__ == "__main__":
    asyncio.run(seed())