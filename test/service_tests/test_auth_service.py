import os
from datetime import datetime

import pytest
from unittest.mock import patch
from jose import jwt
from app.models.user_table import User
from app.schemas.user import UserCreate
from app.models.task_history_table import TaskHistory
from app.exceptions.base_exception import ServiceException
from app.schemas.user import TokenResponse
from app.services.auth_service import AuthService
from app.utils.password_utils import PasswordUtils


@pytest.mark.asyncio
async def test_register_user(auth_service, user_data):
    data = user_data.model_dump()
    data['hashed_password'] = PasswordUtils.get_password_hash(data['password'])
    data.pop('password')
    with patch.object(auth_service.user_service, 'create_user', return_value=User(id=1, **data)):
        user = await auth_service.register(user_data)
        assert user.id == 1
        assert user.email == user_data.email


@pytest.mark.asyncio
async def test_authenticate_success(auth_service):
    raw_password = "secret"
    hashed = PasswordUtils.get_password_hash(raw_password)

    user = User(id=1, username="tester", hashed_password=hashed)
    auth_service.user_crud.get_user_by_username.return_value = user

    result = await auth_service.authenticate("tester", raw_password)

    assert isinstance(result, TokenResponse)
    assert result.token_type == "bearer"
    assert result.access_token


@pytest.mark.asyncio
async def test_authenticate_invalid_password(auth_service):
    user = User(id=1, username="tester", hashed_password=PasswordUtils.get_password_hash("correct"))
    auth_service.user_crud.get_user_by_username.return_value = user

    with pytest.raises(ServiceException, match="Invalid credentials"):
        await auth_service.authenticate("tester", "wrong")


@pytest.mark.asyncio
async def test_authenticate_unknown_user(auth_service):
    auth_service.user_crud.get_user_by_username.return_value = None

    with pytest.raises(ServiceException, match="Invalid credentials"):
        await auth_service.authenticate("nouser", "any")


def test_create_access_token(auth_service):
    token = auth_service.create_access_token(data={"sub": "testuser"})

    secret = os.getenv("SECRET_KEY")
    algorithm = os.getenv("ALGORITHM", "HS256")

    decoded = jwt.decode(token, secret, algorithms=[algorithm])

    assert decoded["sub"] == "testuser"
    assert "exp" in decoded


@patch("app.services.auth_service.redis_client.exists", return_value=False)
def test_verify_token_success(mock_redis_exists, auth_service):
    token = auth_service.create_access_token(data={"sub": "verifyme"})
    result = auth_service.verify_token(token)

    assert result == "verifyme"
    mock_redis_exists.assert_called_once()



def test_verify_token_invalid_signature(auth_service):
    token = jwt.encode({"sub": "hacker"}, "WRONG_KEY", algorithm="HS256")

    with pytest.raises(ServiceException, match="Invalid token"):
        auth_service.verify_token(token)


@patch("app.services.auth_service.redis_client")
def test_logout_sets_redis_flag(mock_redis, auth_service):

    secret = os.getenv("SECRET_KEY")
    algorithm = os.getenv("ALGORITHM", "HS256")
    token = auth_service.create_access_token(data={"sub": "logmeout"})
    payload = jwt.decode(token, secret, algorithm)
    exp = payload["exp"]

    auth_service.logout(token)

    ttl = exp - int(payload["exp"])
    mock_redis.expire.assert_called_once()


@patch("app.services.auth_service.redis_client")
def test_logout_sets_expire(mock_redis, auth_service):
    token = auth_service.create_access_token(data={"sub": "logmeout"})

    payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM", "HS256")])
    exp = int(payload["exp"])
    now = int(datetime.now().timestamp())
    expected_ttl = exp - now

    auth_service.logout(token)

    mock_redis.expire.assert_called_once()

    called_key, called_value = mock_redis.expire.call_args[0][:2]
    called_ex = mock_redis.expire.call_args[1]["ex"]

    assert called_key == f"access_token:{token}"
    assert called_value == "true"
    assert abs(called_ex - expected_ttl) <= 2