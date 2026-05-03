from pathlib import Path
import sys

from fastapi.testclient import TestClient


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.main import app


def make_upload_request(**overrides) -> dict:
    data = {
        "project_title": "测试短剧：雨夜重逢",
        "source_type": "script_docx",
        "project_id": "PROJECT_001",
        "workspace_id": "WORKSPACE_UPLOAD_001",
        "user_id": "USER_001",
        "ai_account_id": "AI_ACCOUNT_001",
        "language": "zh",
        "extra_requirements": "按场景拆分。",
        "metadata": {"context_policy": "current_project_only"},
    }
    data.update(overrides)
    return data


def test_upload_script_endpoint_returns_200() -> None:
    client = TestClient(app)

    response = client.post("/api/uploads/script", json=make_upload_request())

    assert response.status_code == 200


def test_upload_script_endpoint_response_contains_main_fields() -> None:
    client = TestClient(app)

    response = client.post("/api/uploads/script", json=make_upload_request())
    data = response.json()

    assert data["source_id"]
    assert data["project_title"] == "测试短剧：雨夜重逢"
    assert data["extracted_text"]
    assert data["metadata"]


def test_upload_script_endpoint_metadata_extraction_status_is_succeeded() -> None:
    client = TestClient(app)

    response = client.post("/api/uploads/script", json=make_upload_request())
    data = response.json()

    assert data["metadata"]["extraction_status"] == "succeeded"


def test_upload_script_endpoint_extracted_text_length_matches_text() -> None:
    client = TestClient(app)

    response = client.post("/api/uploads/script", json=make_upload_request())
    data = response.json()

    assert data["metadata"]["extracted_text_length"] == len(data["extracted_text"])


def test_upload_script_endpoint_keeps_context_identifiers() -> None:
    client = TestClient(app)

    response = client.post("/api/uploads/script", json=make_upload_request())
    data = response.json()

    assert data["metadata"]["project_id"] == "PROJECT_001"
    assert data["metadata"]["workspace_id"] == "WORKSPACE_UPLOAD_001"
    assert data["metadata"]["user_id"] == "USER_001"
    assert data["metadata"]["ai_account_id"] == "AI_ACCOUNT_001"


def test_upload_script_endpoint_generation_mode_is_mock() -> None:
    client = TestClient(app)

    response = client.post("/api/uploads/script", json=make_upload_request())
    data = response.json()

    assert data["metadata"]["metadata"]["generation_mode"] == "mock"


def test_upload_script_endpoint_default_docx_mock_has_no_warnings() -> None:
    client = TestClient(app)

    response = client.post("/api/uploads/script", json=make_upload_request())
    data = response.json()

    assert data["warnings"] == []


def test_upload_script_endpoint_empty_project_title_returns_422() -> None:
    client = TestClient(app)

    response = client.post("/api/uploads/script", json=make_upload_request(project_title="   "))

    assert response.status_code == 422
