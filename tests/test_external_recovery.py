from uuid import uuid4

from test_web_api import client, create_task, finish  # noqa: F401


def test_recovery_creates_linked_unconfirmed_task_and_preserves_original(client):  # noqa: F811
    parent_id = create_task(client)
    before = client.get(f"/api/v1/tasks/{parent_id}").json()
    request = {
        "request_id": str(uuid4()),
        "expected_revision": before["revision"],
        "action": "restart_external_acquisition",
        "input": {"confirmed": True},
    }
    response = client.post(f"/api/v1/tasks/{parent_id}/actions", json=request)
    assert response.status_code == 202, response.text
    operation = finish(client, response.json())
    assert operation["status"] == "completed", operation
    child_id = operation["result"]["session_id"]
    assert child_id != parent_id
    child = client.get(f"/api/v1/tasks/{child_id}").json()
    assert child["workspace"]["action"] == "confirm_task"
    assert client.get(f"/api/v1/tasks/{parent_id}").json() == before
    repeated = client.post(f"/api/v1/tasks/{parent_id}/actions", json=request).json()
    assert repeated["result"]["session_id"] == child_id
