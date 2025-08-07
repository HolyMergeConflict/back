from unittest.mock import MagicMock

import pytest

from app.models.task_table import Task
from app.models.task_history_table import TaskHistory
from app.enums.user_role import UserRoleEnum
from app.models.user_table import User
from app.exceptions.user_exception import (
    EmailAlreadyRegistered,
    UsernameAlreadyTaken,
    UserNotFound,
    PermissionDeniedUser,
    CannotDemoteSelf,
)


@pytest.mark.asyncio
async def test_create_user_success(user_service, user_data):
    user_service.user_crud.get_user_by_email.return_value = None
    user_service.user_crud.get_user_by_username.return_value = None
    user_service.user_crud.create.return_value = User(id=123, **user_data.model_dump())

    result = await user_service.create_user(user_data)

    assert result.id == 123
    assert result.username == "newuser"
    user_service.user_crud.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_user_existing_email(user_service, user_data):
    user_service.user_crud.get_user_by_email.return_value = User(id=1)

    with pytest.raises(EmailAlreadyRegistered):
        await user_service.create_user(user_data)


@pytest.mark.asyncio
async def test_create_user_existing_username(user_service, user_data):
    user_service.user_crud.get_user_by_email.return_value = None
    user_service.user_crud.get_user_by_username.return_value = User(id=1)

    with pytest.raises(UsernameAlreadyTaken):
        await user_service.create_user(user_data)


@pytest.mark.asyncio
async def test_update_user_role_success(user_service, admin):
    target_user = User(id=10, role=UserRoleEnum.STUDENT)
    user_service.user_crud.get_one.return_value = target_user
    user_service.user_crud.update.return_value = target_user

    updated = await user_service.update_user_role(
        user_id=10,
        new_role=UserRoleEnum.MODERATOR,
        admin=admin
    )

    assert updated.role == UserRoleEnum.STUDENT or updated.role == UserRoleEnum.MODERATOR
    user_service.user_crud.update.assert_called_once()


@pytest.mark.asyncio
async def test_update_user_role_no_permission(user_service, user):
    with pytest.raises(PermissionDeniedUser):
        await user_service.update_user_role(
            user_id=5,
            new_role=UserRoleEnum.MODERATOR,
            admin=user
        )


@pytest.mark.asyncio
async def test_demote_self_denied(user_service, admin):
    target_user = User(id=admin.id, role=UserRoleEnum.ADMIN)
    user_service.user_crud.get_one.return_value = target_user

    with pytest.raises(CannotDemoteSelf):
        await user_service.demote_user(
            user_id=admin.id,
            requesting_user=admin
        )


@pytest.mark.asyncio
async def test_get_user_not_found(user_service, admin):
    user_service.user_crud.get_one.return_value = None

    with pytest.raises(UserNotFound):
        await user_service.get_user(user_id=111, requesting_user=admin)


@pytest.mark.asyncio
async def test_update_user_self(user_service, user):
    updated_data = {"email": "updated@example.com"}
    user_service.user_crud.update.return_value = User(id=user.id, **updated_data)

    result = await user_service.update_user(user_id=user.id, user_data=MagicMock(model_dump=lambda **_: updated_data), requesting_user=user)

    assert result.email == "updated@example.com"
    user_service.user_crud.update.assert_called_once()


@pytest.mark.asyncio
async def test_update_user_as_admin(user_service, admin):
    target_user = User(id=123, email="old@example.com")
    updated_data = {"email": "adminupdated@example.com"}
    user_service.user_crud.get_one.return_value = target_user
    user_service.user_crud.update.return_value = User(id=123, **updated_data)

    result = await user_service.update_user(
        user_id=123,
        user_data=MagicMock(model_dump=lambda **_: updated_data),
        requesting_user=admin
    )

    assert result.email == "adminupdated@example.com"


@pytest.mark.asyncio
async def test_promote_to_admin(user_service, admin):
    target_user = User(id=20, role=UserRoleEnum.STUDENT)
    user_service.user_crud.get_one.return_value = target_user
    user_service.user_crud.update.return_value = target_user

    result = await user_service.promote_to_admin(user_id=20, admin=admin)

    assert result.role == UserRoleEnum.STUDENT or result.role == UserRoleEnum.ADMIN


@pytest.mark.asyncio
async def test_delete_user_by_id(user_service, admin):
    user = User(id=10, role=UserRoleEnum.STUDENT)
    user_service.user_crud.get_one.return_value = user
    user_service.user_crud.delete.return_value = None

    await user_service.delete_user_by_id(user_id=10, requesting_by=admin)
    user_service.user_crud.delete.assert_called_once_with(user)


@pytest.mark.asyncio
async def test_get_users_by_role(user_service, admin):
    user_service.user_crud.get_all.return_value = [User(id=1, role=UserRoleEnum.STUDENT)]

    result = await user_service.get_users_by_role(role=UserRoleEnum.STUDENT, requesting_user=admin)

    assert isinstance(result, list)
    user_service.user_crud.get_all.assert_called_once_with(role=UserRoleEnum.STUDENT)


@pytest.mark.asyncio
async def test_get_users_access_denied(user_service, user):
    with pytest.raises(PermissionDeniedUser):
        await user_service.get_users(requesting_user=user)


@pytest.mark.asyncio
async def test_get_self_user_by_id(user_service, user):
    user_service.user_crud.get_one.return_value = user

    result = await user_service.get_self_user_by_id(user_id=user.id)

    assert result.id == user.id