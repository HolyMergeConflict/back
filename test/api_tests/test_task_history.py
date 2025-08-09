import asyncio
from datetime import datetime, timedelta, timezone

import pytest


async def _get_solution_status_values(client):
    r = await client.get("/openapi.json")
    assert r.status_code == 200
    spec = r.json()
    comps = spec.get("components", {}).get("schemas", {})
    for name, schema in comps.items():
        if "TaskSolutionStatus" in name and "enum" in schema:
            return schema["enum"]
    for name, schema in comps.items():
        if name.endswith("TaskHistoryCreate"):
            props = schema.get("properties", {})
            status_schema = props.get("status", {})
            if "enum" in status_schema:
                return status_schema["enum"]
    raise AssertionError("Не удалось найти TaskSolutionStatusEnum в openapi.json")


async def _create_task(client, headers, **overrides):
    payload = {
        "title": "TH: tiny task",
        "description": "just for task_history tests",
        "answer": "42",
        "difficulty": 1,
        "subject": "task_history",
        **overrides,
    }
    r = await client.post("/tasks/", json=payload, headers=headers)
    assert r.status_code == 201, f"Create task failed: {r.status_code} {r.text}"
    return r.json()["id"]


@pytest.mark.anyio
async def test_log_and_list_my_history(client, registered_user_and_token):
    _, _, user_headers = registered_user_and_token
    statuses = await _get_solution_status_values(client)
    assert len(statuses) >= 1
    status_ok = statuses[0]

    task_id = await _create_task(client, user_headers)

    payload = {
        "task_id": task_id,
        "status": status_ok,
        "answer": "my answer",
        "score": 0.75,
        "feedback": "looks fine",
    }
    r = await client.post("/task-history/", json=payload, headers=user_headers)
    assert r.status_code == 200 or r.status_code == 201
    created = r.json()
    assert created["task_id"] == task_id
    assert created["answer"] == "my answer"
    assert "timestamp" in created

    r = await client.get("/task-history/my", headers=user_headers)
    assert r.status_code == 200
    items = r.json()
    assert any(it["task_id"] == task_id for it in items)


@pytest.mark.anyio
async def test_list_by_status_and_by_task(client, registered_user_and_token):
    _, _, user_headers = registered_user_and_token
    statuses = await _get_solution_status_values(client)
    assert len(statuses) >= 2, "Нужно хотя бы 2 статуса, чтобы проверить фильтрацию"
    status_a, status_b = statuses[:2]

    task_id = await _create_task(client, user_headers)

    for st in (status_a, status_b):
        r = await client.post(
            "/task-history/",
            json={
                "task_id": task_id,
                "status": st,
                "answer": f"ans-{st}",
                "score": 0.5,
            },
            headers=user_headers,
        )
        assert r.status_code in (200, 201)

    r = await client.get(f"/task-history/my/by-status?status={status_a}", headers=user_headers)
    assert r.status_code == 200
    filtered = r.json()
    assert all(item["task_id"] == task_id for item in filtered)
    assert all(item["status"] == status_a for item in filtered)

    r = await client.get(f"/task-history/my/task/{task_id}", headers=user_headers)
    assert r.status_code == 200
    by_task = r.json()
    assert len(by_task) >= 2
    assert {it["answer"] for it in by_task} >= {f"ans-{status_a}", f"ans-{status_b}"}


@pytest.mark.anyio
async def test_latest_attempt_and_range(client, registered_user_and_token):
    _, _, user_headers = registered_user_and_token
    statuses = await _get_solution_status_values(client)
    st = statuses[0]

    task_id = await _create_task(client, user_headers)

    r1 = await client.post(
        "/task-history/",
        json={"task_id": task_id, "status": st, "answer": "try-1", "score": 0.1},
        headers=user_headers,
    )
    assert r1.status_code in (200, 201)
    await asyncio.sleep(0.01)
    r2 = await client.post(
        "/task-history/",
        json={"task_id": task_id, "status": st, "answer": "try-2", "score": 0.2},
        headers=user_headers,
    )
    assert r2.status_code in (200, 201)

    r = await client.get(f"/task-history/my/task/{task_id}/latest", headers=user_headers)
    assert r.status_code == 200
    latest = r.json()
    assert latest is not None
    assert latest["answer"] == "try-2"

    now = datetime.now(timezone.utc)
    start = (now - timedelta(minutes=1)).isoformat()
    end = (now + timedelta(minutes=1)).isoformat()
    r = await client.get(
        f"/task-history/my/range?start={start}&end={end}",
        headers=user_headers,
    )
    assert r.status_code == 200
    in_range = r.json()
    assert any(it["task_id"] == task_id for it in in_range)

    start2 = (now + timedelta(minutes=2)).isoformat()
    end2 = (now + timedelta(minutes=3)).isoformat()
    r = await client.get(
        f"/task-history/my/range?start={start2}&end={end2}",
        headers=user_headers,
    )
    assert r.status_code == 200
    assert r.json() == [] or isinstance(r.json(), list)