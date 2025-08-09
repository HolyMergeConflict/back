import pytest

@pytest.mark.anyio
async def test_student_creates_task_and_admin_moderates(client, registered_user_and_token, admin_user_and_token):
    user_data, _, user_headers = registered_user_and_token
    _, _, admin_headers = admin_user_and_token

    task_payload = {
        "title": "Sum two numbers",
        "description": "Return a+b",
        "answer": "def solve(a,b): return a+b",
        "difficulty": 1,
        "subject": "algorithms"
    }
    res = await client.post("/tasks/", json=task_payload, headers=user_headers)
    assert res.status_code == 201
    created = res.json()
    task_id = created["id"]
    assert created["status"] in ("pending", "PENDING")

    res = await client.get("/tasks/moderation", headers=admin_headers)
    assert res.status_code == 200
    moderation_list = res.json()
    assert any(t["id"] == task_id for t in moderation_list)

    res = await client.patch(f"/tasks/{task_id}/approve", headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["status"] in ("approved", "APPROVED")

    res = await client.get(f"/tasks/{task_id}", headers=user_headers)
    assert res.status_code == 200
    assert res.json()["id"] == task_id


@pytest.mark.anyio
async def test_non_moderator_cannot_approve_or_delete(client, registered_user_and_token):
    _, _, user_headers = registered_user_and_token

    res = await client.post("/tasks/", json={
        "title": "XOR",
        "description": "Return a^b",
        "answer": "def solve(a,b): return a^b",
        "difficulty": 1,
        "subject": "algorithms"
    }, headers=user_headers)
    assert res.status_code == 201
    task_id = res.json()["id"]

    res = await client.patch(f"/tasks/{task_id}/approve", headers=user_headers)
    assert res.status_code in (401, 403)

    res = await client.delete(f"/tasks/{task_id}", headers=user_headers)
    assert res.status_code in (401, 403)


@pytest.mark.anyio
async def test_creator_can_update_task_but_other_user_cannot(client, registered_user_and_token):
    _, _, headers_u1 = registered_user_and_token
    res = await client.post("/tasks/", json={
        "title": "Reverse string",
        "description": "Return s[::-1]",
        "answer": "def solve(s): return s[::-1]",
        "difficulty": 1,
        "subject": "strings"
    }, headers=headers_u1)
    assert res.status_code == 201
    task_id = res.json()["id"]

    res = await client.put(f"/tasks/{task_id}", json={"title": "Reverse string fast"}, headers=headers_u1)
    assert res.status_code == 200
    assert res.json()["title"] == "Reverse string fast"

    from uuid import uuid4
    suf = uuid4().hex[:8]
    user2 = {
        "username": f"user2_{suf}",
        "email": f"user2_{suf}@ex.com",
        "password": "pwd",
        "role": "student",
    }
    r = await client.post("/auth/register", json=user2)
    assert r.status_code == 201
    r = await client.post("/auth/login", json={"username": user2["username"], "password": user2["password"]})
    assert r.status_code == 200
    headers_u2 = {"Authorization": f"Bearer {r.json()['access_token']}"}

    res = await client.put(f"/tasks/{task_id}", json={"title": "Hacked"}, headers=headers_u2)
    assert res.status_code in (401, 403)



@pytest.mark.anyio
async def test_student_creates_task_and_admin_moderates(client, registered_user_and_token, admin_user_and_token):
    _, _, user_headers = registered_user_and_token
    _, _, admin_headers = admin_user_and_token

    payload = {
        "title": "Sum two numbers",
        "description": "Return a+b",
        "answer": "def solve(a,b): return a+b",
        "difficulty": 1,
        "subject": "algorithms"
    }


    res = await client.post("/tasks/", json=payload, headers=user_headers)
    assert res.status_code == 201


    res = await client.get("/tasks/my_tasks", headers=user_headers)
    assert res.status_code == 200
    my_tasks = res.json()
    task = next(t for t in my_tasks if t["title"] == payload["title"])
    task_id = task["id"]
    assert task["status"].lower() == "pending"


    res = await client.get("/tasks/moderation", headers=admin_headers)
    assert res.status_code == 200
    assert any(t["id"] == task_id for t in res.json())


    res = await client.patch(f"/tasks/{task_id}/approve", headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["status"].lower() == "approved"


    res = await client.get(f"/tasks/{task_id}", headers=user_headers)
    assert res.status_code == 200
    assert res.json()["id"] == task_id


@pytest.mark.anyio
async def test_student_cannot_get_pending_task_by_id(client, registered_user_and_token):
    _, _, user_headers = registered_user_and_token

    payload = {
        "title": "Hidden pending",
        "description": "should be hidden until approve",
        "answer": "print(42)",
        "difficulty": 1,
        "subject": "misc"
    }
    res = await client.post("/tasks/", json=payload, headers=user_headers)
    assert res.status_code == 201

    res = await client.get("/tasks/my_tasks", headers=user_headers)
    assert res.status_code == 200
    task_id = next(t["id"] for t in res.json() if t["title"] == payload["title"])


    res = await client.get(f"/tasks/{task_id}", headers=user_headers)
    assert res.status_code == 403  # PermissionDeniedTask


@pytest.mark.anyio
async def test_only_moderator_can_approve_reject_delete(client, registered_user_and_token, admin_user_and_token):
    _, _, user_headers = registered_user_and_token
    _, _, admin_headers = admin_user_and_token

    payload = {
        "title": "Needs moderation",
        "description": "moderation checks",
        "answer": "ok()",
        "difficulty": 2,
        "subject": "checks"
    }
    res = await client.post("/tasks/", json=payload, headers=user_headers)
    assert res.status_code == 201
    res = await client.get("/tasks/my_tasks", headers=user_headers)
    task_id = next(t["id"] for t in res.json() if t["title"] == payload["title"])


    res = await client.patch(f"/tasks/{task_id}/approve", headers=user_headers)
    assert res.status_code == 403


    res = await client.patch(f"/tasks/{task_id}/reject", headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["status"].lower() == "rejected"


    res = await client.delete(f"/tasks/{task_id}", headers=admin_headers)
    assert res.status_code == 204


@pytest.mark.anyio
async def test_update_task_owner_and_moderator(client, registered_user_and_token, admin_user_and_token):
    _, _, user_headers = registered_user_and_token
    _, _, admin_headers = admin_user_and_token

    payload = {
        "title": "Updatable",
        "description": "to be updated",
        "answer": "x=1",
        "difficulty": 1,
        "subject": "upd"
    }
    res = await client.post("/tasks/", json=payload, headers=user_headers)
    assert res.status_code == 201

    res = await client.get("/tasks/my_tasks", headers=user_headers)
    task_id = next(t["id"] for t in res.json() if t["title"] == payload["title"])


    res = await client.put(f"/tasks/{task_id}", json={"title": "Updatable edited"}, headers=user_headers)
    assert res.status_code == 200
    assert res.json()["title"] == "Updatable edited"



    suffix = "zzz"
    other_user = {
        "username": f"other_{suffix}",
        "email": f"other_{suffix}@ex.com",
        "password": "p",
        "role": "student"
    }

    res = await client.post("/auth/register", json=other_user)
    assert res.status_code == 201
    res = await client.post("/auth/login", json={"username": other_user["username"], "password": other_user["password"]})
    other_headers = {"Authorization": f"Bearer {res.json()['access_token']}"}

    res = await client.put(f"/tasks/{task_id}", json={"title": "Hacked"}, headers=other_headers)
    assert res.status_code == 403


    res = await client.put(f"/tasks/{task_id}", json={"title": "Moderator edited"}, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["title"] == "Moderator edited"


@pytest.mark.anyio
async def test_tasks_filters_and_visibility(client, registered_user_and_token, admin_user_and_token):
    _, _, user_headers = registered_user_and_token
    _, _, admin_headers = admin_user_and_token


    for i in range(2):
        res = await client.post("/tasks/", json={
            "title": f"Vis{i}",
            "description": "filter me",
            "answer": "ok",
            "difficulty": 1,
            "subject": "filters"
        }, headers=user_headers)
        assert res.status_code == 201


    res = await client.get("/tasks/?task_status=pending", headers=admin_headers)
    assert res.status_code == 200
    pending_ids = {t["id"] for t in res.json() if t["subject"] == "filters"}
    assert len(pending_ids) >= 2


    one_id = next(iter(pending_ids))
    res = await client.patch(f"/tasks/{one_id}/approved", headers=admin_headers)
    assert res.status_code == 200


    res = await client.get("/tasks/?task_status=approved", headers=user_headers)
    assert res.status_code == 200
    approved_ids = {t["id"] for t in res.json()}
    assert one_id in approved_ids


    res = await client.get("/tasks/?task_status=pending", headers=user_headers)
    assert res.status_code == 200
    student_pending = {t["id"] for t in res.json()}

    assert one_id in approved_ids
    assert student_pending == set()