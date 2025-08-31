import pytest

@pytest.mark.anyio
async def test_user_cannot_update_other_user(client, registered_user_and_token):
    user_data, _, headers = registered_user_and_token
    res = await client.put("/users/9999", json={"email": "hacker@example.com"}, headers=headers)
    assert res.status_code in (403, 404)


@pytest.mark.anyio
async def test_user_cannot_change_own_role(client, registered_user_and_token):
    user_data, _, headers = registered_user_and_token
    me = await client.get("/users/me", headers=headers)
    user_id = me.json()["id"]
    res = await client.patch(f"/users/{user_id}/role", json={"role": "admin"}, headers=headers)
    assert res.status_code == 403


@pytest.mark.anyio
async def test_guest_cannot_access_users(client):
    res = await client.get("/users/")
    assert res.status_code == 401


@pytest.mark.anyio
async def test_guest_cannot_update_user(client):
    res = await client.put("/users/1", json={"email": "unauth@example.com"})
    assert res.status_code == 401


'''
@pytest.mark.anyio
async def test_invalid_token_cannot_access(client):
    headers = {"Authorization": "Bearer invalid.token.here"}
    res = await client.get("/users/me", headers=headers)

    assert res.status_code == 401
    assert res.json()["detail"] == "Invalid token"
'''