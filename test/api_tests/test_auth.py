import pytest

from app.enums.user_role import UserRoleEnum


@pytest.mark.anyio
async def test_register_and_login(client):
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "securepassword",
        "role": UserRoleEnum.STUDENT
    }

    res = await client.post("/auth/register", json=user_data)
    assert res.status_code == 201
    assert res.json()["username"] == user_data["username"]

    # login
    res = await client.post("/auth/login", json={
        "username": user_data["username"],
        "password": user_data["password"]
    })



    assert res.status_code == 200
    token = res.json()["access_token"]
    assert token is not None



    # protected route
    res = await client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["email"] == user_data["email"]