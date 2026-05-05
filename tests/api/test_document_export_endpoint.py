from pathlib import Path
import json
import sys

from fastapi.testclient import TestClient


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.main import app  # noqa: E402


def make_export_request(**overrides) -> dict:
    data = {
        "project_title": "测试短剧：灯火归来",
        "document_type": "short_drama_script",
        "source_stage": "script",
        "content_text": "第一集：林灯回到旧楼，发现父亲留下的剧本。",
        "structured_payload": None,
        "export_format": "txt",
        "filename": "script.txt",
        "metadata": {"edited": True},
    }
    data.update(overrides)
    return data


def test_export_endpoint_txt_returns_200() -> None:
    client = TestClient(app)

    response = client.post("/api/documents/export", json=make_export_request())

    assert response.status_code == 200


def test_export_endpoint_txt_response_contains_contract() -> None:
    client = TestClient(app)

    response = client.post("/api/documents/export", json=make_export_request())
    data = response.json()

    assert data["export_format"] == "txt"
    assert data["filename"].endswith(".txt")
    assert "测试短剧：灯火归来" in data["content_text"]
    assert "林灯回到旧楼" in data["content_text"]
    assert data["download_url"] is None
    assert data["file_size_bytes"] > 0


def test_export_endpoint_json_returns_parseable_json_content() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/documents/export",
        json=make_export_request(
            export_format="json",
            filename="script.json",
            structured_payload={
                "project_title": "测试短剧：灯火归来",
                "logline": "年轻编剧回到旧楼。",
            },
        ),
    )
    data = response.json()
    parsed = json.loads(data["content_text"])

    assert response.status_code == 200
    assert data["export_format"] == "json"
    assert parsed["project_title"] == "测试短剧：灯火归来"
    assert parsed["logline"] == "年轻编剧回到旧楼。"


def test_export_endpoint_json_keeps_chinese_readable() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/documents/export",
        json=make_export_request(
            export_format="json",
            structured_payload={"logline": "年轻编剧回到旧楼。"},
        ),
    )
    data = response.json()

    assert response.status_code == 200
    assert "年轻编剧回到旧楼" in data["content_text"]
    assert "\\u" not in data["content_text"]


def test_export_endpoint_accepts_context_options_and_returns_metadata_context() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/documents/export",
        json=make_export_request(
            context_options={
                "project_id": "project_lights_return",
                "session_id": "session_export_review",
                "context_policy": "current_project_only",
            },
        ),
    )
    data = response.json()

    assert response.status_code == 200
    assert data["metadata"]["context_policy"] == "current_project_only"
    assert data["metadata"]["context"]["project_id"] == "project_lights_return"
    assert data["metadata"]["context"]["session_id"] == "session_export_review"


def test_export_endpoint_keeps_only_safe_filename() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/documents/export",
        json=make_export_request(filename="/Users/example/secret/script.docx"),
    )
    data = response.json()

    assert response.status_code == 200
    assert data["filename"] == "script.txt"
    assert "/Users/example" not in data["filename"]
    assert "/" not in data["filename"]


def test_export_endpoint_docx_returns_clear_error() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/documents/export",
        json=make_export_request(export_format="docx", filename="script.docx"),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "DOCX export is not implemented yet."


def test_export_endpoint_response_does_not_include_local_path_fields() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/documents/export",
        json=make_export_request(
            export_format="json",
            structured_payload={
                "project_title": "测试短剧：灯火归来",
                "server_path": "/Users/example/secret",
                "nested": {"local_path": "/tmp/secret"},
            },
            metadata={
                "absolute_path": "/Users/example/secret",
                "edited": True,
            },
        ),
    )
    response_text = json.dumps(response.json(), ensure_ascii=False)

    assert response.status_code == 200
    assert "server_path" not in response_text
    assert "local_path" not in response_text
    assert "absolute_path" not in response_text
    assert "/Users/example" not in response_text


def test_openapi_contains_export_route() -> None:
    client = TestClient(app)

    response = client.get("/openapi.json")
    data = response.json()

    assert response.status_code == 200
    assert "/api/documents/export" in data["paths"]
