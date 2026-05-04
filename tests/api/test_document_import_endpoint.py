from pathlib import Path
import sys

from fastapi.testclient import TestClient


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.main import app  # noqa: E402


def make_import_preview_request(**overrides) -> dict:
    data = {
        "filename": "old-bookstore.docx",
        "extracted_text": "旧书店来信\n第一章，女主回到旧书店。",
        "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "file_size_bytes": 2048,
        "source_type": "docx",
        "project_title": "测试短剧：旧书店来信",
        "checksum": "safe-checksum",
    }
    data.update(overrides)
    return data


def test_import_preview_endpoint_returns_200() -> None:
    client = TestClient(app)

    response = client.post("/api/documents/import-preview", json=make_import_preview_request())

    assert response.status_code == 200


def test_import_preview_endpoint_response_contains_preview_contract() -> None:
    client = TestClient(app)

    response = client.post("/api/documents/import-preview", json=make_import_preview_request())
    data = response.json()

    assert data["status"] == "preview_ready"
    assert data["project_title"] == "测试短剧：旧书店来信"
    assert data["next_required_action"] == "user_confirm_import_action"
    assert data["preview"]["source"]["filename"] == "old-bookstore.docx"
    assert data["preview"]["extracted_text"] == "旧书店来信\n第一章，女主回到旧书店。"
    assert data["preview"]["preview_text"] == "旧书店来信\n第一章，女主回到旧书店。"


def test_import_preview_endpoint_marks_truncated_preview_for_long_text() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/documents/import-preview",
        json=make_import_preview_request(extracted_text="雨" * 1200),
    )
    data = response.json()

    assert response.status_code == 200
    assert data["preview"]["metadata"]["safe_preview_truncated"] is True
    assert len(data["preview"]["preview_text"]) < len(data["preview"]["extracted_text"])


def test_import_preview_endpoint_keeps_only_safe_filename() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/documents/import-preview",
        json=make_import_preview_request(filename="/Users/example/Documents/private-novel.docx"),
    )
    data = response.json()

    assert response.status_code == 200
    assert data["preview"]["source"]["filename"] == "private-novel.docx"
    assert "/Users/example" not in data["preview"]["source"]["filename"]


def test_import_preview_endpoint_missing_filename_returns_422() -> None:
    client = TestClient(app)
    payload = make_import_preview_request()
    payload.pop("filename")

    response = client.post("/api/documents/import-preview", json=payload)

    assert response.status_code == 422


def test_import_preview_endpoint_missing_extracted_text_returns_422() -> None:
    client = TestClient(app)
    payload = make_import_preview_request()
    payload.pop("extracted_text")

    response = client.post("/api/documents/import-preview", json=payload)

    assert response.status_code == 422


def test_import_preview_endpoint_negative_file_size_returns_422() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/documents/import-preview",
        json=make_import_preview_request(file_size_bytes=-1),
    )

    assert response.status_code == 422


def test_openapi_contains_import_preview_route() -> None:
    client = TestClient(app)

    response = client.get("/openapi.json")
    data = response.json()

    assert response.status_code == 200
    assert "/api/documents/import-preview" in data["paths"]
