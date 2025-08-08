from fastapi import HTTPException, status, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.db.CRUD.user import UserCRUD
from app.models.user_table import User


async def get_current_user(
        request: Request,
        db: AsyncSession = Depends(get_db)
) -> User:
    username = getattr(request.state, "username", None)
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    user_crud = UserCRUD(db)
    user = await user_crud.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user
