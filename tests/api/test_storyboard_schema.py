from pathlib import Path
import sys

import pytest
from pydantic import ValidationError


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.schemas.storyboard import (
    SceneStoryboard,
    ShotStoryboard,
    StoryboardInput,
    StoryboardOutput,
)


def make_valid_shot(**overrides) -> ShotStoryboard:
    data = {
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
    data.update(overrides)
    return ShotStoryboard(**data)


def make_valid_scene(**overrides) -> SceneStoryboard:
    data = {
        "scene_id": "S001",
        "scene_number": 1,
        "location": "医院门口",
        "time": "雨夜",
        "scene_summary": "林晚和顾沉在雨夜医院门口重逢。",
        "scene_conflict": "顾沉试图确认林晚回来的目的，林晚保持距离。",
        "shots": [make_valid_shot()],
    }
    data.update(overrides)
    return SceneStoryboard(**data)


def test_storyboard_input_rejects_empty_project_title() -> None:
    with pytest.raises(ValidationError):
        StoryboardInput(project_title="", script_text="第1集 第1场｜医院门口｜雨夜。")


def test_storyboard_input_rejects_empty_script_text() -> None:
    with pytest.raises(ValidationError):
        StoryboardInput(project_title="测试短剧：雨夜重逢", script_text="")


def test_storyboard_output_rejects_empty_scenes() -> None:
    with pytest.raises(ValidationError):
        StoryboardOutput(
            project_title="测试短剧：雨夜重逢",
            episode_number=1,
            storyboard_summary="雨夜重逢分镜。",
            scenes=[],
        )


def test_scene_storyboard_rejects_empty_shots() -> None:
    with pytest.raises(ValidationError):
        make_valid_scene(shots=[])


def test_shot_storyboard_rejects_empty_visual_description() -> None:
    with pytest.raises(ValidationError):
        make_valid_shot(visual_description="")


def test_shot_storyboard_rejects_non_positive_duration_seconds() -> None:
    with pytest.raises(ValidationError):
        make_valid_shot(duration_seconds=0)
