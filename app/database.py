import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from dotenv import load_dotenv
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

load_dotenv()

URL = os.getenv('SQL_URL')

engine = create_async_engine(URL, echo=False, future=True)
SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


@asynccontextmanager
async def get_db_context():
    db_gen = get_db()
    db = await anext(db_gen)
    try:
        yield db
    finally:
        await db_gen.aclose()