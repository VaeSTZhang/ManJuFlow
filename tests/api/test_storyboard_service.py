import json
from pathlib import Path
import sys


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.schemas.storyboard import StoryboardInput
from app.services import storyboard_service
from app.services.storyboard_service import generate_storyboard, generate_storyboard_mock


def make_storyboard_input() -> StoryboardInput:
    return StoryboardInput(
        project_title="测试短剧：雨夜重逢",
        script_text="第1集 第1场｜医院门口｜雨夜。林晚和顾沉在雨中重逢。",
    )


def patch_storyboard_generation_mode(monkeypatch, mode: str) -> None:
    class FakeSettings:
        storyboard_generation_mode = mode

    monkeypatch.setattr(storyboard_service, "get_settings", lambda: FakeSettings())


def make_storyboard_output_data() -> dict:
    return {
        "project_title": "测试短剧：雨夜重逢",
        "episode_number": 1,
        "storyboard_summary": "雨夜医院门口重逢，情绪从压抑到对峙。",
        "scenes": [
            {
                "scene_id": "S001",
                "scene_number": 1,
                "location": "医院门口",
                "time": "雨夜",
                "scene_summary": "林晚和顾沉在雨夜医院门口重逢。",
                "scene_conflict": "顾沉试图确认林晚回来的目的，林晚保持距离。",
                "shots": [
                    {
                        "shot_id": "S001_SH001",
                        "shot_number": 1,
                        "scene_number": 1,
                        "shot_type": "中景",
                        "camera_angle": "平视",
                        "camera_movement": "固定",
                        "subject": "林晚和顾沉",
                        "action": "两人在雨中隔着医院门口对视。",
                        "environment": "雨夜医院门口，地面反射车灯。",
                        "lighting": "冷色雨夜光与车灯交错。",
                        "emotion": "压抑、重逢、试探",
                        "dialogue": "顾沉：你终于肯回来了？",
                        "duration_seconds": 4,
                        "visual_description": "雨夜医院门口，林晚撑着黑伞站在台阶边，顾沉从车里下来，两人在雨幕和冷色车灯中对视。",
                        "visual_notes": "中景保持两人距离，雨幕强化压抑情绪。",
                        "ai_image_prompt_hint": "雨夜医院门口，黑伞，男女对视，冷色车灯，现实主义电影感。",
                    }
                ],
            }
        ],
    }


def test_generate_storyboard_mock_includes_stable_storyboard_fields() -> None:
    input_data = make_storyboard_input()

    result = generate_storyboard_mock(input_data)

    assert result.project_title == "测试短剧：雨夜重逢"
    assert len(result.scenes) >= 1

    first_scene = result.scenes[0]
    assert first_scene.scene_id
    assert first_scene.scene_id.startswith("S")
    assert len(first_scene.shots) >= 1

    first_shot = first_scene.shots[0]
    assert first_shot.shot_id
    assert first_scene.scene_id in first_shot.shot_id
    assert isinstance(first_shot.visual_description, str)
    assert first_shot.visual_description.strip()
    assert isinstance(first_shot.ai_image_prompt_hint, str)
    assert first_shot.ai_image_prompt_hint.strip()


def test_generate_storyboard_uses_mock_mode(monkeypatch) -> None:
    patch_storyboard_generation_mode(monkeypatch, "mock")
    input_data = make_storyboard_input()

    result = generate_storyboard(input_data)

    assert result.project_title == "测试短剧：雨夜重逢"
    assert len(result.scenes) >= 1
    first_shot = result.scenes[0].shots[0]
    assert first_shot.shot_id
    assert first_shot.visual_description.strip()


def test_generate_storyboard_llm_mode_uses_llm_client(monkeypatch) -> None:
    patch_storyboard_generation_mode(monkeypatch, "llm")
    returned_messages = []

    class FakeLLMClient:
        def chat(self, messages):
            returned_messages.extend(messages)
            return json.dumps(make_storyboard_output_data(), ensure_ascii=False)

    monkeypatch.setattr(storyboard_service, "LLMClient", FakeLLMClient)
    input_data = make_storyboard_input()

    result = generate_storyboard(input_data)

    assert result.project_title == "测试短剧：雨夜重逢"
    assert returned_messages
    assert returned_messages[0]["role"] == "system"
    assert returned_messages[1]["role"] == "user"
    assert "测试短剧：雨夜重逢" in returned_messages[1]["content"]
    assert result.scenes[0].scene_id == "S001"
    first_shot = result.scenes[0].shots[0]
    assert first_shot.shot_id == "S001_SH001"
    assert first_shot.visual_description.strip()


def test_generate_storyboard_rejects_invalid_mode(monkeypatch) -> None:
    patch_storyboard_generation_mode(monkeypatch, "invalid")
    input_data = make_storyboard_input()

    try:
        generate_storyboard(input_data)
    except ValueError as exc:
        message = str(exc)
        assert "STORYBOARD_GENERATION_MODE" in message
        assert "mock" in message
        assert "llm" in message
    else:
        raise AssertionError("generate_storyboard should reject invalid storyboard generation mode.")
