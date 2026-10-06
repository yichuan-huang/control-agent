from __future__ import annotations

import json
import re
from threading import Event
from uuid import uuid4

from web_api_helpers import api_client, finish

from cfdc.web.errors import APIError


def test_web_locale_is_explicit_and_errors_have_reusable_message_refs(tmp_path):
    with api_client(tmp_path) as client:
        english = client.get("/api/v1/cases/does-not-exist?locale=en")
        chinese = client.get("/api/v1/cases/does-not-exist?locale=zh-CN")
        assert english.status_code == chinese.status_code == 404
        en, zh = english.json()["error"], chinese.json()["error"]
        assert en["code"] == zh["code"] == "case_not_found"
        assert en["message"] == "This built-in case was not found."
        assert zh["message"] == "未找到此内置案例。"
        assert en["message_ref"] == zh["message_ref"]
        assert en["message_ref"]["key"] == "web.error.case_not_found"
        assert client.get("/api/v1/cases?locale=fr").status_code == 422
        assert client.get("/api/v1/cases/does-not-exist").json()["error"] == zh


def test_locale_switch_preserves_raw_case_task_revision_and_download(tmp_path):
    with api_client(tmp_path) as client:
        en_case = client.get("/api/v1/cases/dc_motor_speed_v1?locale=en").json()
        zh_case = client.get("/api/v1/cases/dc_motor_speed_v1?locale=zh-CN").json()
        assert en_case["task"] == zh_case["task"]
        assert en_case["draft"] == zh_case["draft"]
        assert not re.search(r"[\u4e00-\u9fff]", en_case["title"])
        assert en_case["title"] != zh_case["title"]
        body = {
            "request_id": str(uuid4()),
            "task": en_case["task"],
            "case_id": "dc_motor_speed_v1",
            "use_rag": False,
        }
        op = finish(client, client.post("/api/v1/tasks?locale=en", json=body))
        assert op["status"] == "completed"
        task_id = op["session_id"]
        path = f"/api/v1/tasks/{task_id}"
        before = client.get(f"{path}/downloads/report").content
        english = client.get(f"{path}?locale=en").json()
        chinese = client.get(f"{path}?locale=zh-CN").json()
        assert english["revision"] == chinese["revision"]
        assert english["task"] == chinese["task"]
        assert english["workspace"]["action"] == chinese["workspace"]["action"]
        assert english["workspace"]["title"] != chinese["workspace"]["title"]
        assert client.get(f"{path}/downloads/report?locale=en").content == before
        replay = client.post("/api/v1/tasks?locale=zh-CN", json=body).json()
        assert replay["operation_id"] == op["operation_id"]


def test_settings_and_early_middleware_errors_use_requested_locale(tmp_path):
    with api_client(tmp_path) as client:
        result = client.post("/api/v1/config/probe?locale=en", json={}).json()
        assert result["connected"] is False
        assert result["message"] == "Enter the model URL, name, and API key."
        assert result["message_ref"]["key"] == "web.probe.required"
        rejected = client.post(
            "/api/v1/tasks?locale=en",
            headers={"origin": "https://foreign.example"},
            json={},
        )
        assert rejected.status_code == 403
        assert not re.search(r"[\u4e00-\u9fff]", rejected.json()["error"]["message"])
        oversize = client.post(
            "/api/v1/uploads?locale=en",
            content=b"x",
            headers={"content-length": str(129 * 1024 * 1024)},
        )
        assert oversize.status_code == 413
        assert "128 MiB" in oversize.json()["error"]["message"]
        assert not re.search(r"[\u4e00-\u9fff]", oversize.json()["error"]["message"])


def test_doctor_http_localizes_without_changing_cli_contract(tmp_path):
    with api_client(tmp_path) as client:
        en = client.post(
            "/api/v1/config/doctor?locale=en", json={"use_rag": False}
        ).json()
        zh = client.post(
            "/api/v1/config/doctor?locale=zh-CN", json={"use_rag": False}
        ).json()
        assert not re.search(r"[\u4e00-\u9fff]", json.dumps(en, ensure_ascii=False))
        assert en["checks"][0]["message"] != zh["checks"][0]["message"]
        assert en["checks"][0]["message_ref"] == zh["checks"][0]["message_ref"]


def test_running_action_captures_locale_and_retry_does_not_execute_twice(
    tmp_path, monkeypatch
):
    entered, release = Event(), Event()
    calls = []

    def execute(state, body, files, *, locale):
        calls.append(locale)
        entered.set()
        assert release.wait(10)
        raise APIError("action_failed", "模型生成未完成。", 422)

    monkeypatch.setattr("cfdc.web.api.execute_action", execute)
    with api_client(tmp_path) as client:
        task = client.get("/api/v1/cases/dc_motor_speed_v1").json()["task"]
        created = finish(
            client,
            client.post(
                "/api/v1/tasks",
                json={
                    "request_id": str(uuid4()),
                    "task": task,
                    "case_id": "dc_motor_speed_v1",
                    "use_rag": False,
                },
            ),
        )
        task_id = created["session_id"]
        revision = created["result"]["revision"]
        body = {
            "request_id": str(uuid4()),
            "expected_revision": revision,
            "action": "confirm_task",
        }
        response = client.post(f"/api/v1/tasks/{task_id}/actions?locale=en", json=body)
        try:
            assert entered.wait(10)
            duplicate = client.post(
                f"/api/v1/tasks/{task_id}/actions?locale=zh-CN", json=body
            )
            assert duplicate.json()["operation_id"] == response.json()["operation_id"]
            assert calls == ["en"]
        finally:
            release.set()
        completed = finish(client, response)
        assert completed["status"] == "failed"
        operation_id = completed["operation_id"]
        stored = tmp_path / "http-runtime" / "operations" / f"{operation_id}.json"
        before = stored.read_bytes()
        en = client.get(f"/api/v1/operations/{operation_id}?locale=en").json()
        zh = client.get(f"/api/v1/operations/{operation_id}?locale=zh-CN").json()
        assert en["error"]["message_ref"] == zh["error"]["message_ref"]
        assert en["error"]["message"] != zh["error"]["message"]
        assert not re.search(r"[\u4e00-\u9fff]", en["error"]["message"])
        assert stored.read_bytes() == before
        assert client.get(f"/api/v1/tasks/{task_id}").json()["revision"] == revision
        assert calls == ["en"]


def test_draft_field_refs_render_both_languages_without_replacing_input(tmp_path):
    with api_client(tmp_path) as client:
        draft = client.get("/api/v1/drafts/default").json()["draft"]
        en = client.post("/api/v1/drafts/validate?locale=en", json={"draft": draft})
        zh = client.post("/api/v1/drafts/validate?locale=zh-CN", json={"draft": draft})
        assert en.status_code == zh.status_code == 422
        en_error, zh_error = en.json()["error"], zh.json()["error"]
        assert en_error["fields"].keys() == zh_error["fields"].keys()
        assert en_error["field_message_refs"] == zh_error["field_message_refs"]
        assert not re.search(
            r"[\u4e00-\u9fff]", json.dumps(en_error, ensure_ascii=False)
        )
        assert en_error["fields"]["description"] != zh_error["fields"]["description"]
