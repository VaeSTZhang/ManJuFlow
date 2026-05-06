from pathlib import Path
import sys

from fastapi.testclient import TestClient
import pytest


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.config import get_settings
from app.main import app


@pytest.fixture(autouse=True)
def force_mock_script_generation_mode(monkeypatch) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "script_generation_mode", "mock")


def make_segment_request(**overrides) -> dict:
    data = {
        "project_title": "测试短剧：雨夜重逢",
        "script_text": "第1场，雨夜医院门口。林晚撑着黑伞站在台阶下，顾沉从黑色轿车中下来。",
        "source_id": "SRC_001",
        "workspace_id": "WS_SCRIPT_SEG_001",
        "user_id": "USER_001",
        "ai_account_id": "AI_ACC_001",
    }
    data.update(overrides)
    return data


def test_segment_script_endpoint_with_script_text_returns_200() -> None:
    client = TestClient(app)

    response = client.post("/api/scripts/segment", json=make_segment_request())

    assert response.status_code == 200


def test_segment_script_endpoint_response_contains_main_fields() -> None:
    client = TestClient(app)

    response = client.post("/api/scripts/segment", json=make_segment_request())
    data = response.json()

    assert data["project_title"] == "测试短剧：雨夜重逢"
    assert data["segmentation_summary"]
    assert data["segment_count"]
    assert isinstance(data["segments"], list)


def test_segment_script_endpoint_segment_count_matches_segments() -> None:
    client = TestClient(app)

    response = client.post("/api/scripts/segment", json=make_segment_request())
    data = response.json()

    assert data["segment_count"] == len(data["segments"])


def test_segment_script_endpoint_returns_at_least_two_segments() -> None:
    client = TestClient(app)

    response = client.post("/api/scripts/segment", json=make_segment_request())
    data = response.json()

    assert len(data["segments"]) >= 2


def test_segment_script_endpoint_segments_contain_required_fields() -> None:
    client = TestClient(app)

    response = client.post("/api/scripts/segment", json=make_segment_request())
    data = response.json()

    for segment in data["segments"]:
        assert segment["segment_id"]
        assert segment["title"]
        assert segment["original_text"]
        assert segment["summary"]


def test_segment_script_endpoint_keeps_context_identifiers() -> None:
    client = TestClient(app)

    response = client.post("/api/scripts/segment", json=make_segment_request())
    data = response.json()

    assert data["source_id"] == "SRC_001"
    assert data["workspace_id"] == "WS_SCRIPT_SEG_001"
    assert data["user_id"] == "USER_001"
    assert data["ai_account_id"] == "AI_ACC_001"


def test_segment_script_endpoint_metadata_generation_mode_is_mock() -> None:
    client = TestClient(app)

    response = client.post("/api/scripts/segment", json=make_segment_request())
    data = response.json()

    assert data["metadata"]["generation_mode"] == "mock"


def test_segment_script_endpoint_with_source_id_without_script_text_returns_200() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/scripts/segment",
        json=make_segment_request(script_text=None, source_id="UPLOAD_SRC_001"),
    )
    data = response.json()

    assert response.status_code == 200
    assert data["source_id"] == "UPLOAD_SRC_001"
    assert data["segments"][0]["original_text"].startswith("Mock extracted text from upload source")


def test_segment_script_endpoint_missing_script_text_and_source_id_returns_422() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/scripts/segment",
        json={"project_title": "测试短剧：雨夜重逢"},
    )

    assert response.status_code == 422


def test_segment_script_endpoint_empty_script_text_returns_422() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/scripts/segment",
        json={"project_title": "测试短剧：雨夜重逢", "script_text": "   "},
    )

    assert response.status_code == 422


def test_existing_generate_script_endpoint_still_available() -> None:
    client = TestClient(app)

    # Compatibility check must stay offline; the fixture forces mock generation.
    response = client.post(
        "/api/scripts/generate",
        json={
            "idea_text": "一个被裁员的中年男人发现公司老板用 AI 伪造财报",
            "script_type": "短剧",
            "genre": "都市悬疑",
            "episode_count": 1,
            "episode_duration": "3-5分钟",
            "target_platform": "短视频平台",
            "tone": "节奏快、反转强",
            "audience": "短剧观众",
            "style_requirements": "开头强冲突，结尾反转",
        },
    )

    assert response.status_code == 200
    assert response.json()["project_title"]


def test_segment_script_endpoint_rejects_script_text_over_limit() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/scripts/segment",
        json=make_segment_request(script_text="a" * 100001),
    )
    data = response.json()

    assert response.status_code == 400
    assert "SCRIPT_TEXT_TOO_LONG" in data["detail"]
    assert "100,000" in data["detail"]
    assert "100,001" in data["detail"]


def test_segment_script_endpoint_rejects_extra_requirements_over_limit() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/scripts/segment",
        json=make_segment_request(extra_requirements="a" * 2001),
    )
    data = response.json()

    assert response.status_code == 400
    assert "EXTRA_REQUIREMENTS_TOO_LONG" in data["detail"]
