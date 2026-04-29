from pathlib import Path
import sys

from fastapi.testclient import TestClient


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.main import app


def make_request_payload() -> dict:
    return {
        "project_title": "测试短剧：雨夜重逢",
        "storyboard_summary": "雨夜医院门口重逢，情绪从压抑到对峙。",
        "storyboard_text": "S001_SH001 雨夜医院门口，林晚撑着黑伞站在台阶边，顾沉从车里下来，两人在雨幕和冷色车灯中对视。",
        "target_model": "general",
        "aspect_ratio": "9:16",
        "style_preset": "cinematic realistic",
        "language": "en",
    }


def test_generate_image_prompt_endpoint_returns_stable_prompt_fields() -> None:
    client = TestClient(app)

    response = client.post("/api/prompts/generate", json=make_request_payload())

    assert response.status_code == 200

    data = response.json()
    assert data["project_title"] == "测试短剧：雨夜重逢"
    assert data["prompt_summary"]
    assert isinstance(data["items"], list)
    assert len(data["items"]) >= 2

    for item in data["items"]:
        assert item["prompt_id"]
        assert item["shot_id"]
        assert item["positive_prompt"]
        assert item["negative_prompt"]
        assert "low quality" in item["negative_prompt"]
        assert "blurry" in item["negative_prompt"]
        assert "watermark" in item["negative_prompt"]


def test_generate_image_prompt_endpoint_is_available_in_openapi() -> None:
    client = TestClient(app)

    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/api/prompts/generate" in response.json()["paths"]
