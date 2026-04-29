from pathlib import Path
import sys


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.schemas.storyboard import StoryboardInput
from app.services.storyboard_service import generate_storyboard_mock


def test_generate_storyboard_mock_includes_stable_storyboard_fields() -> None:
    input_data = StoryboardInput(
        project_title="测试短剧：雨夜重逢",
        script_text="第1集 第1场｜医院门口｜雨夜。林晚和顾沉在雨中重逢。",
    )

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
