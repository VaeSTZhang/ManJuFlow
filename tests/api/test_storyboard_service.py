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


def test_generate_storyboard_llm_mode_falls_back_to_mock_for_now(monkeypatch) -> None:
    # 当前阶段 llm 模式临时 fallback 到 mock；接入真实 LLM 后可更新此测试。
    patch_storyboard_generation_mode(monkeypatch, "llm")
    input_data = make_storyboard_input()

    result = generate_storyboard(input_data)

    assert len(result.scenes) >= 1
    first_shot = result.scenes[0].shots[0]
    assert first_shot.ai_image_prompt_hint
    assert first_shot.ai_image_prompt_hint.strip()


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
