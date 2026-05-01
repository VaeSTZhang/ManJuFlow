from pathlib import Path
import sys

import pytest
from pydantic import ValidationError


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.schemas.image_prompt import (
    ImagePromptInput,
    ImagePromptItem,
    ImagePromptOutput,
)


def make_valid_image_prompt_item_data(**overrides) -> dict:
    data = {
        "prompt_id": "P001",
        "shot_id": "S001_SH001",
        "scene_id": "S001",
        "shot_number": 1,
        "scene_number": 1,
        "source_visual_description": "雨夜医院门口，男女主角在冷色车灯中对视。",
        "positive_prompt": "cinematic realistic rain night hospital entrance, two characters facing each other, cold headlights",
        "negative_prompt": "low quality, blurry, distorted hands, extra fingers, text, watermark",
        "camera_language": "medium shot, eye-level angle",
        "lighting": "cold rain ambience with car headlights",
        "color_palette": "blue gray, muted red highlights",
        "character_consistency": "same actors, consistent wardrobe and facial features",
        "environment": "hospital entrance in heavy rain",
        "composition": "two characters separated by foreground rain, balanced frame",
        "model_hint": "general image generation model",
        "seed": 12345,
        "notes": "Keep realistic facial proportions.",
    }
    data.update(overrides)
    return data


def make_valid_image_prompt_item(**overrides) -> ImagePromptItem:
    data = make_valid_image_prompt_item_data(**overrides)
    return ImagePromptItem(**data)


def test_image_prompt_input_accepts_storyboard_text_source() -> None:
    data = ImagePromptInput(
        project_title="测试短剧：雨夜重逢",
        storyboard_text="S001_SH001 雨夜医院门口，男女主角在冷色车灯中对视。",
    )

    assert data.project_title == "测试短剧：雨夜重逢"
    assert data.storyboard_text is not None


def test_image_prompt_input_accepts_optional_request_level_llm_provider_and_model() -> None:
    data = ImagePromptInput(
        project_title="测试短剧：雨夜重逢",
        storyboard_text="S001_SH001 雨夜医院门口，男女主角在冷色车灯中对视。",
        llm_provider="kimi",
        llm_model="kimi-k2.5",
    )

    assert data.llm_provider == "kimi"
    assert data.llm_model == "kimi-k2.5"


def test_image_prompt_input_keeps_old_request_shape_compatible() -> None:
    data = ImagePromptInput(
        project_title="测试短剧：雨夜重逢",
        storyboard_text="S001_SH001 雨夜医院门口，男女主角在冷色车灯中对视。",
    )

    assert data.llm_provider is None
    assert data.llm_model is None


def test_image_prompt_item_required_fields_are_valid() -> None:
    item = make_valid_image_prompt_item()

    assert item.prompt_id == "P001"
    assert item.positive_prompt
    assert item.negative_prompt


def test_image_prompt_output_accepts_multiple_items() -> None:
    output = ImagePromptOutput(
        project_title="测试短剧：雨夜重逢",
        prompt_summary="为雨夜重逢场景生成两条绘图 Prompt。",
        items=[
            make_valid_image_prompt_item(prompt_id="P001", shot_id="S001_SH001"),
            make_valid_image_prompt_item(prompt_id="P002", shot_id="S001_SH002", shot_number=2),
        ],
    )

    assert len(output.items) == 2


def test_image_prompt_output_model_dump_contains_main_fields() -> None:
    output = ImagePromptOutput(
        project_title="测试短剧：雨夜重逢",
        prompt_summary="为雨夜重逢场景生成绘图 Prompt。",
        items=[make_valid_image_prompt_item()],
    )

    data = output.model_dump()

    assert data["project_title"] == "测试短剧：雨夜重逢"
    assert data["prompt_summary"] == "为雨夜重逢场景生成绘图 Prompt。"
    assert len(data["items"]) == 1


def test_image_prompt_item_requires_positive_prompt() -> None:
    data = make_valid_image_prompt_item_data()
    data.pop("positive_prompt")

    with pytest.raises(ValidationError):
        ImagePromptItem(**data)


def test_image_prompt_item_requires_negative_prompt() -> None:
    data = make_valid_image_prompt_item_data()
    data.pop("negative_prompt")

    with pytest.raises(ValidationError):
        ImagePromptItem(**data)
