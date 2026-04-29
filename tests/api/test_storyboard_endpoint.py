from pathlib import Path
import sys

from fastapi.testclient import TestClient


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.main import app
from app.services import storyboard_service


def test_generate_storyboard_endpoint_returns_stable_storyboard_fields(monkeypatch) -> None:
    class FakeSettings:
        storyboard_generation_mode = "mock"

    monkeypatch.setattr(storyboard_service, "get_settings", lambda: FakeSettings())
    client = TestClient(app)

    response = client.post(
        "/api/storyboards/generate",
        json={
            "project_title": "测试短剧：雨夜重逢",
            "script_text": "第1集 第1场｜医院门口｜雨夜。林晚和顾沉在雨中重逢。",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["project_title"] == "测试短剧：雨夜重逢"
    assert isinstance(data["scenes"], list)
    assert len(data["scenes"]) >= 1

    first_scene = data["scenes"][0]
    assert first_scene["scene_id"]
    assert isinstance(first_scene["shots"], list)
    assert len(first_scene["shots"]) >= 1

    first_shot = first_scene["shots"][0]
    assert first_shot["shot_id"]
    assert first_shot["visual_description"]
    assert first_shot["visual_description"].strip()
    assert first_shot["ai_image_prompt_hint"]
    assert first_shot["ai_image_prompt_hint"].strip()
