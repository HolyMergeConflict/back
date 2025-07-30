from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User

def register_user(db: Session, user_data: dict) -> User:
    if get_user_by_email(db, user_data['email']):
        raise HTTPException(status_code=400, detail='email already registered')
    if get_user_by_username(db, user_data['username']):
        raise HTTPException(status_code=400, detail='username is already taken')

    user = User(**user_data)

    return create_user(db, user)


def get_user_profile(db: Session, username: str) -> User:
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(
            status_code=404,
            detail='user not found'
        )
    return user

def update_user_profile(db: Session, user: User, data: dict) -> User:
    return update_user(db, user, data)

def delete_user(db: Session, user: User) -> None:
    delete_user(db, user)