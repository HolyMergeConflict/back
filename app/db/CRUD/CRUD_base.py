import abc
from typing import TypeVar, Type, Generic, cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession as Session
from sqlalchemy import delete as sqlalchemy_delete

T = TypeVar("T")

class CRUDBase(Generic[T], abc.ABC):
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model


    async def get_query(self, **filters):
        stmt = select(self.model).filter_by(**filters)
        return await self.db.execute(stmt)


    async def get_one(self, **filters) -> T | None:
        result = await self.get_query(**filters)
        return result.scalars().first()


    async def get_all(self, *conditions, **filters) -> list[T]:
        stmt = select(self.model).filter_by(**filters)
        if conditions:
            stmt = stmt.filter(*conditions)
        result = await self.db.execute(stmt)
        return result.scalars().all()


    async def create(self, obj: T) -> T:
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj


    async def update(self, obj: T, data: dict) -> T:
        for key, value in data.items():
            setattr(obj, key, value)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj



    async def delete_by_filter(self, **filters) -> int:
        stmt = sqlalchemy_delete(self.model).filter_by(**filters)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return cast(int, result.rowcount)


    async def delete(self, obj: T) -> None:
        await self.db.delete(obj)
        await self.db.commit()
