from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.database import get_db
from app.utils.redis_client import redis_client

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    status = {"api": "ok"}

    try:
        await db.execute(text("SELECT 1"))
        status["database"] = "ok"
    except Exception as e:
        status["database"] = f"error: {e}"

    try:
        pong = await redis_client.ping()
        status["redis"] = "ok" if pong else "error"
    except Exception as e:
        status["redis"] = f"error: {e}"

    overall = all(v == "ok" for v in status.values())
    status["status"] = "ok" if overall else "error"
    return status
