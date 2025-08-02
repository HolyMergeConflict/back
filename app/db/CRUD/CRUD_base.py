import abc
from typing import TypeVar, Type, Generic

from sqlalchemy.orm import Session

T = TypeVar("T")

class CRUDBase(Generic[T], abc.ABC):
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model


    def get_query(self, **filters):
        return self.db.query(self.model).filter_by(**filters)


    def get_one(self, **filters) -> T | None:
        return self.get_query(**filters).first()


    def get_all(self, *conditions, **filters) -> list[T]:
        query = self.get_query(**filters)
        if conditions:
            query = query.filter(*conditions)
        return query.all()


    def create(self, obj: T) -> T:
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj


    def update(self, obj: T, data: dict) -> T:
        for key, value in data.items():
            setattr(obj, key, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj


    def delete_by_filter(self, **filters) -> int:
        result = self.db.query(self.model).filter_by(**filters).delete(synchronize_session=False)
        self.db.commit()
        return result


    def delete(self, obj: T) -> None:
        self.db.delete(obj)
        self.db.commit()
