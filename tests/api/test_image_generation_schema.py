from pathlib import Path
import sys

import pytest
from pydantic import ValidationError


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.schemas.image_generation import (
    ImageGenerationInput,
    ImageGenerationItem,
    ImageGenerationOutput,
    ImageGenerationPromptItem,
)


def make_valid_generation_prompt_item_data(**overrides) -> dict:
    data = {
        "prompt_id": "P001",
        "shot_id": "S001_SH001",
        "positive_prompt": "cinematic realistic rain night hospital entrance, two characters facing each other",
        "negative_prompt": "low quality, blurry, distorted hands, watermark",
        "style_preset": "cinematic realistic",
        "aspect_ratio": "9:16",
        "model_hint": "general image generation model",
        "seed": 12345,
        "metadata": {"scene_id": "S001"},
    }
    data.update(overrides)
    return data


def make_valid_generation_prompt_item(**overrides) -> ImageGenerationPromptItem:
    return ImageGenerationPromptItem(**make_valid_generation_prompt_item_data(**overrides))


def make_valid_generation_item(**overrides) -> ImageGenerationItem:
    data = {
        "task_id": "IMG_TASK_001",
        "prompt_id": "P001",
        "shot_id": "S001_SH001",
        "positive_prompt": "cinematic realistic rain night hospital entrance, two characters facing each other",
        "negative_prompt": "low quality, blurry, distorted hands, watermark",
        "mock_url": "/mock/images/P001.png",
        "width": 1024,
        "height": 1820,
        "seed": 12345,
    }
    data.update(overrides)
    return ImageGenerationItem(**data)


def test_image_generation_prompt_item_can_be_created() -> None:
    item = make_valid_generation_prompt_item()

    assert item.prompt_id == "P001"
    assert item.shot_id == "S001_SH001"
    assert item.metadata["scene_id"] == "S001"


def test_image_generation_input_can_be_created_with_project_title_and_prompt_items() -> None:
    data = ImageGenerationInput(
        project_title="测试短剧：雨夜重逢",
        prompt_items=[make_valid_generation_prompt_item()],
    )

    assert data.project_title == "测试短剧：雨夜重逢"
    assert len(data.prompt_items) == 1


def test_image_generation_input_defaults_to_mock_provider() -> None:
    data = ImageGenerationInput(
        project_title="测试短剧：雨夜重逢",
        prompt_items=[make_valid_generation_prompt_item()],
    )

    assert data.provider == "mock"


def test_image_generation_input_defaults_to_mock_workflow_name() -> None:
    data = ImageGenerationInput(
        project_title="测试短剧：雨夜重逢",
        prompt_items=[make_valid_generation_prompt_item()],
    )

    assert data.workflow_name == "mock_image_generation_v1"


def test_image_generation_input_defaults_output_count_to_one() -> None:
    data = ImageGenerationInput(
        project_title="测试短剧：雨夜重逢",
        prompt_items=[make_valid_generation_prompt_item()],
    )

    assert data.output_count == 1


def test_image_generation_input_requires_prompt_items() -> None:
    with pytest.raises(ValidationError):
        ImageGenerationInput(project_title="测试短剧：雨夜重逢")


def test_image_generation_input_rejects_empty_prompt_items() -> None:
    with pytest.raises(ValidationError):
        ImageGenerationInput(project_title="测试短剧：雨夜重逢", prompt_items=[])


def test_image_generation_input_rejects_output_count_less_than_one() -> None:
    with pytest.raises(ValidationError):
        ImageGenerationInput(
            project_title="测试短剧：雨夜重逢",
            prompt_items=[make_valid_generation_prompt_item()],
            output_count=0,
        )


def test_image_generation_input_rejects_output_count_greater_than_four() -> None:
    with pytest.raises(ValidationError):
        ImageGenerationInput(
            project_title="测试短剧：雨夜重逢",
            prompt_items=[make_valid_generation_prompt_item()],
            output_count=5,
        )


def test_image_generation_item_can_include_mock_url() -> None:
    item = make_valid_generation_item(mock_url="/mock/images/P001.png")

    assert item.mock_url == "/mock/images/P001.png"


def test_image_generation_output_can_include_multiple_items() -> None:
    output = ImageGenerationOutput(
        project_title="测试短剧：雨夜重逢",
        items=[
            make_valid_generation_item(task_id="IMG_TASK_001", prompt_id="P001", shot_id="S001_SH001"),
            make_valid_generation_item(task_id="IMG_TASK_002", prompt_id="P002", shot_id="S001_SH002"),
        ],
    )

    assert len(output.items) == 2


def test_image_generation_output_model_dump_contains_main_fields() -> None:
    output = ImageGenerationOutput(
        project_title="测试短剧：雨夜重逢",
        items=[make_valid_generation_item()],
    )

    data = output.model_dump()

    assert data["project_title"] == "测试短剧：雨夜重逢"
    assert data["provider"] == "mock"
    assert data["status"] == "succeeded"
    assert len(data["items"]) == 1
