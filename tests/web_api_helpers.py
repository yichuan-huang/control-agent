"""Real HTTP helpers for migrated Kernel workflow regression tests."""

from contextlib import contextmanager
from time import monotonic, sleep
from uuid import uuid4

from fastapi.testclient import TestClient

from cfdc.web.api import create_app


@contextmanager
def api_client(tmp_path, **kwargs):
    app = create_app(
        session_dir=tmp_path,
        runtime_dir=tmp_path / "http-runtime",
        prepare_rag=False,
        **kwargs,
    )
    with TestClient(app, base_url="http://127.0.0.1:7860") as client:
        yield client


def finish(client, response):
    assert response.status_code == 202, response.text
    operation = response.json()
    deadline = monotonic() + 30
    while operation["status"] in {"queued", "running"}:
        assert monotonic() < deadline, operation
        sleep(0.01)
        operation = client.get(f"/api/v1/operations/{operation['operation_id']}").json()
    return operation


def action(client, state, name, *, request_id=None, **input):
    return client.post(
        f"/api/v1/tasks/{state['kernel_session_id']}/actions",
        json={
            "request_id": request_id or str(uuid4()),
            "expected_revision": state["kernel_revision"],
            "action": name,
            "input": input,
        },
    )


def create(client, *, draft=None, task=None, **kwargs):
    source = {"draft": draft} if draft is not None else {"task": task}
    operation = finish(
        client,
        client.post(
            "/api/v1/tasks",
            json={
                "request_id": str(uuid4()),
                **source,
                "confirmed": True,
                "use_rag": False,
                **kwargs,
            },
        ),
    )
    assert operation["status"] == "completed", operation
    return operation["session_id"]
