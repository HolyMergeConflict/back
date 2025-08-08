import pytest


@pytest.mark.anyio
async def test_get_self_user(client, registered_user_and_token):
    _, _, headers = registered_user_and_token

    res = await client.get("/users/me", headers=headers)
    assert res.status_code == 200
    assert "email" in res.json()


@pytest.mark.anyio
async def test_update_self_user(client, registered_user_and_token):
    user_data, _, headers = registered_user_and_token

    # Получаем текущего пользователя
    me = await client.get("/users/me", headers=headers)
    user_id = me.json()["id"]

    # Обновляем email
    updated_email = "new1@example.com"
    res = await client.put(f"/users/{user_id}", json={"email": updated_email}, headers=headers)
    assert res.status_code == 200
    assert res.json()["email"] == updated_email


@pytest.mark.anyio
async def test_admin_can_change_user_role(client, registered_user_and_token, admin_user_and_token):
    user_data, _, _ = registered_user_and_token
    _, _, admin_headers = admin_user_and_token

    res = await client.get("/users/", headers=admin_headers)
    print("RESPONSE STATUS:", res.status_code)
    print("RESPONSE TEXT:", res.text)

    assert res.status_code == 200, "Failed to get user list"
    user_list = res.json()

    user_id = next(u["id"] for u in user_list if u["username"] == user_data["username"])

    # Меняем роль пользователя на teacher
    res = await client.patch(f"/users/{user_id}/role", json={"role": "teacher"}, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["role"] == "teacher"


@pytest.mark.anyio
async def test_get_users_by_role(client, admin_user_and_token):
    _, _, admin_headers = admin_user_and_token

    res = await client.get("/users/", params={"role": "moderator"}, headers=admin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)
    for user in res.json():
        assert user["role"] == "moderator"


@pytest.mark.anyio
async def test_admin_can_delete_user(client, registered_user_and_token, admin_user_and_token):
    user_data, _, _ = registered_user_and_token
    _, _, admin_headers = admin_user_and_token

    # Получаем ID пользователя
    res = await client.get("/users/", headers=admin_headers)
    user_list = res.json()
    user = next((u for u in user_list if u["username"] == user_data["username"]), None)
    assert user is not None
    user_id = user["id"]

    res = await client.delete(f"/users/{user_id}", headers=admin_headers)
    assert res.status_code == 204


@pytest.mark.anyio
async def test_admin_can_promote_to_moderator(client, registered_user_and_token, admin_user_and_token):
    user_data, _, _ = registered_user_and_token
    _, _, admin_headers = admin_user_and_token

    res = await client.get("/users/", headers=admin_headers)
    user = next(u for u in res.json() if u["username"] == user_data["username"])
    user_id = user["id"]

    res = await client.patch(f"/users/{user_id}/promote/moderator", headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["role"] == "moderator"


@pytest.mark.anyio
async def test_admin_can_demote_user(client, registered_user_and_token, admin_user_and_token):
    user_data, _, _ = registered_user_and_token
    _, _, admin_headers = admin_user_and_token

    res = await client.get("/users/", headers=admin_headers)
    user = next(u for u in res.json() if u["username"] == user_data["username"])
    user_id = user["id"]

    res = await client.patch(f"/users/{user_id}/demote", params={"new_role": "student"}, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["role"] == "student"
