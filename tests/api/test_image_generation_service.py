from pathlib import Path
import sys


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.schemas.image_generation import (
    ImageGenerationInput,
    ImageGenerationOutput,
    ImageGenerationPromptItem,
)
from app.services.image_generation_service import (
    generate_image_generation,
    generate_image_generation_mock,
)


NEGATIVE_PROMPT = "low quality, blurry, distorted hands, watermark"


def make_prompt_item(**overrides) -> ImageGenerationPromptItem:
    data = {
        "prompt_id": "P001",
        "shot_id": "S001_SH001",
        "positive_prompt": "cinematic realistic rain night hospital entrance, two characters facing each other",
        "negative_prompt": NEGATIVE_PROMPT,
        "style_preset": "cinematic realistic",
        "aspect_ratio": "9:16",
        "seed": 100,
    }
    data.update(overrides)
    return ImageGenerationPromptItem(**data)


def make_generation_input(**overrides) -> ImageGenerationInput:
    data = {
        "project_title": "测试短剧：雨夜重逢",
        "prompt_items": [make_prompt_item()],
    }
    data.update(overrides)
    return ImageGenerationInput(**data)


def test_generate_image_generation_mock_returns_output_schema() -> None:
    result = generate_image_generation_mock(make_generation_input())

    assert isinstance(result, ImageGenerationOutput)


def test_generate_image_generation_mock_keeps_project_title() -> None:
    input_data = make_generation_input()

    result = generate_image_generation_mock(input_data)

    assert result.project_title == input_data.project_title


def test_generate_image_generation_mock_defaults_to_mock_provider() -> None:
    result = generate_image_generation_mock(make_generation_input())

    assert result.provider == "mock"


def test_generate_image_generation_mock_status_is_succeeded() -> None:
    result = generate_image_generation_mock(make_generation_input())

    assert result.status == "succeeded"
    assert result.items[0].status == "succeeded"


def test_generate_image_generation_mock_creates_one_item_for_single_prompt_and_output_count_one() -> None:
    result = generate_image_generation_mock(make_generation_input(output_count=1))

    assert len(result.items) == 1


def test_generate_image_generation_mock_expands_prompt_items_by_output_count() -> None:
    input_data = make_generation_input(
        prompt_items=[
            make_prompt_item(prompt_id="P001", shot_id="S001_SH001"),
            make_prompt_item(prompt_id="P002", shot_id="S001_SH002"),
        ],
        output_count=2,
    )

    result = generate_image_generation_mock(input_data)

    assert len(result.items) == 4
    assert [item.task_id for item in result.items] == [
        "mock-img-P001-1",
        "mock-img-P001-2",
        "mock-img-P002-1",
        "mock-img-P002-2",
    ]


def test_generate_image_generation_mock_items_include_required_identifiers_and_paths() -> None:
    result = generate_image_generation_mock(make_generation_input())
    item = result.items[0]

    assert item.task_id
    assert item.prompt_id == "P001"
    assert item.shot_id == "S001_SH001"
    assert item.mock_url
    assert item.local_path


def test_generate_image_generation_mock_uses_safe_mock_url_and_local_path_prefixes() -> None:
    result = generate_image_generation_mock(make_generation_input())
    item = result.items[0]

    assert item.mock_url is not None
    assert item.mock_url.startswith("/mock/images/")
    assert item.local_path is not None
    assert item.local_path.startswith("mock_outputs/images/")


def test_generate_image_generation_mock_keeps_negative_prompt() -> None:
    result = generate_image_generation_mock(make_generation_input())

    assert result.items[0].negative_prompt == NEGATIVE_PROMPT


def test_generate_image_generation_mock_defaults_9_16_to_vertical_dimensions() -> None:
    result = generate_image_generation_mock(make_generation_input())
    item = result.items[0]

    assert item.width == 1080
    assert item.height == 1920


def test_generate_image_generation_mock_uses_16_9_dimensions() -> None:
    result = generate_image_generation_mock(
        make_generation_input(prompt_items=[make_prompt_item(aspect_ratio="16:9")])
    )
    item = result.items[0]

    assert item.width == 1920
    assert item.height == 1080


def test_generate_image_generation_mock_uses_1_1_dimensions() -> None:
    result = generate_image_generation_mock(
        make_generation_input(prompt_items=[make_prompt_item(aspect_ratio="1:1")])
    )
    item = result.items[0]

    assert item.width == 1024
    assert item.height == 1024


def test_generate_image_generation_currently_returns_mock_output() -> None:
    result = generate_image_generation(make_generation_input())

    assert isinstance(result, ImageGenerationOutput)
    assert result.provider == "mock"
    assert result.items[0].mock_url is not None
    assert result.items[0].metadata["source"] == "mock"


def test_generate_image_generation_mock_metadata_source_is_mock() -> None:
    result = generate_image_generation_mock(make_generation_input())

    assert result.metadata["source"] == "mock"
    assert result.items[0].metadata["source"] == "mock"


def test_generate_image_generation_mock_does_not_call_external_services() -> None:
    result = generate_image_generation_mock(make_generation_input())

    assert result.items[0].image_url is None
    assert result.items[0].mock_url == "/mock/images/mock-img-P001-1.png"
    assert result.items[0].metadata["note"] == (
        "Mock image generation result. No real GPU or ComfyUI call was made."
    )
