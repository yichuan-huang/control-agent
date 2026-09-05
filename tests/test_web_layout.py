from fastapi.testclient import TestClient

from cfdc.web import api


def test_default_static_root_follows_web_package_not_working_directory(
    tmp_path, monkeypatch
):
    package = tmp_path / "source" / "cfdc" / "web"
    static = package / "frontend" / "dist"
    static.mkdir(parents=True)
    (static / "index.html").write_text("<html>relocated shell</html>")
    (static / "app.js").write_text("window.relocated = true;")
    monkeypatch.setattr(api, "__file__", str(package / "api.py"))
    monkeypatch.chdir(tmp_path)
    application = api.create_app(
        session_dir=tmp_path / "sessions",
        runtime_dir=tmp_path / "runtime",
        prepare_rag=False,
    )
    with TestClient(application, base_url="http://127.0.0.1") as client:
        assert client.get("/").text == "<html>relocated shell</html>"
        assert client.get("/tasks/a-record").text == "<html>relocated shell</html>"
        assert client.get("/app.js").text == "window.relocated = true;"
        assert client.get("/api/not-an-endpoint").status_code == 404


def test_case_api_keeps_numbered_and_audit_catalog_order(tmp_path):
    application = api.create_app(
        session_dir=tmp_path / "sessions",
        runtime_dir=tmp_path / "runtime",
        prepare_rag=False,
    )
    with TestClient(application, base_url="http://127.0.0.1") as client:
        items = client.get("/api/v1/cases").json()["items"]
    engineering = [item for item in items if item["category"] == "engineering"]
    assert [item["title"].split("｜")[0] for item in engineering] == [
        "01",
        "02",
        "03",
        "04",
        "05",
        "06",
        "07",
        "08",
        "09",
        "10",
        "11",
    ]
    assert [item["id"] for item in items if item["category"] == "audit"] == [
        "audit_class_i_level",
        "audit_class_ii_thermal",
        "audit_class_ii_oscillator",
        "audit_class_iii_motion",
        "audit_class_iv_nmp",
        "audit_class_iv_high_order",
        "audit_class_v_mimo",
    ]
