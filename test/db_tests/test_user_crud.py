import pytest
from datetime import datetime

from app.enums.user_role import UserRoleEnum
from app.models.user_table import User

@pytest.mark.asyncio
async def test_create_user(user_crud):
    user = User(
        username='testuser',
        email='testuser@example.com',
        hashed_password='hashedpassword',
        role=UserRoleEnum.STUDENT
    )
    created = await user_crud.create(user)
    assert created.id is not None
    assert created.username == 'testuser'
    assert created.email == 'testuser@example.com'

@pytest.mark.asyncio
async def test_get_one_user(user_crud):
    user = User(
        username='oneuser',
        email='oneuser@example.com',
        hashed_password='hashedpassword',
        role=UserRoleEnum.STUDENT
    )
    await user_crud.create(user)
    fetched = await user_crud.get_one(username='oneuser')
    assert fetched is not None
    assert fetched.email == 'oneuser@example.com'

@pytest.mark.asyncio
async def test_get_all_users(user_crud):
    await user_crud.create(User(
        username='u1',
        email='u1@example.com',
        hashed_password='pass',
        role=UserRoleEnum.STUDENT
    ))
    await user_crud.create(User(
        username='u2',
        email='u2@example.com',
        hashed_password='pass',
        role=UserRoleEnum.STUDENT
    ))
    users = await user_crud.get_all()
    assert len(users) >= 2

@pytest.mark.asyncio
async def test_update_user(user_crud):
    user = User(
        username='updateuser',
        email='before@example.com',
        hashed_password='pass',
        role=UserRoleEnum.STUDENT
    )
    created = await user_crud.create(user)
    updated = await user_crud.update(created, {"email": "after@example.com"})
    assert updated.email == "after@example.com"

@pytest.mark.asyncio
async def test_delete_user(user_crud):
    user = User(
        username='todelete',
        email='delete@example.com',
        hashed_password='pass',
        role=UserRoleEnum.STUDENT
    )
    created = await user_crud.create(user)
    await user_crud.delete(created)
    result = await user_crud.get_one(id=created.id)
    assert result is None

@pytest.mark.asyncio
async def test_delete_by_filter_user(user_crud):
    user = User(
        username='filterdelete',
        email='filter@example.com',
        hashed_password='pass',
        role=UserRoleEnum.STUDENT
    )
    await user_crud.create(user)
    count = await user_crud.delete_by_filter(username='filterdelete')
    assert count == 1
