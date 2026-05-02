from pathlib import Path
import sys

import pytest


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.schemas.image_generation import (
    ImageGenerationInput,
    ImageGenerationOutput,
    ImageGenerationPromptItem,
)
from app.services.image_generation_provider import (
    ComfyUIImageGenerationProviderPlaceholder,
    MockImageGenerationProvider,
    get_image_generation_provider,
)
from app.services.image_generation_service import generate_image_generation


def make_prompt_item(**overrides) -> ImageGenerationPromptItem:
    data = {
        "prompt_id": "P001",
        "shot_id": "S001_SH001",
        "positive_prompt": "cinematic realistic rain night hospital entrance, two characters facing each other",
        "negative_prompt": "low quality, blurry, distorted hands, watermark",
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


def test_get_image_generation_provider_returns_mock_provider() -> None:
    provider = get_image_generation_provider("mock")

    assert isinstance(provider, MockImageGenerationProvider)


def test_mock_provider_generate_returns_output_schema() -> None:
    provider = MockImageGenerationProvider()

    result = provider.generate(make_generation_input())

    assert isinstance(result, ImageGenerationOutput)


def test_mock_provider_output_matches_mock_service_structure() -> None:
    provider = MockImageGenerationProvider()

    result = provider.generate(make_generation_input())
    item = result.items[0]

    assert result.project_title == "测试短剧：雨夜重逢"
    assert result.provider == "mock"
    assert result.status == "succeeded"
    assert item.task_id == "mock-img-P001-1"
    assert item.prompt_id == "P001"
    assert item.shot_id == "S001_SH001"
    assert item.mock_url == "/mock/images/mock-img-P001-1.png"
    assert item.local_path == "mock_outputs/images/mock-img-P001-1.png"
    assert item.metadata["source"] == "mock"


def test_get_image_generation_provider_returns_comfyui_placeholder() -> None:
    provider = get_image_generation_provider("comfyui")

    assert isinstance(provider, ComfyUIImageGenerationProviderPlaceholder)


def test_comfyui_placeholder_generate_raises_not_implemented() -> None:
    provider = ComfyUIImageGenerationProviderPlaceholder()

    with pytest.raises(NotImplementedError) as exc_info:
        provider.generate(make_generation_input(provider="comfyui"))

    message = str(exc_info.value)
    assert "ComfyUI" in message
    assert "private deployment" in message


def test_get_image_generation_provider_rejects_unknown_provider() -> None:
    with pytest.raises(ValueError) as exc_info:
        get_image_generation_provider("unknown")

    assert "Unsupported image generation provider" in str(exc_info.value)


def test_generate_image_generation_with_mock_provider_still_returns_mock_output() -> None:
    result = generate_image_generation(make_generation_input(provider="mock"))

    assert isinstance(result, ImageGenerationOutput)
    assert result.provider == "mock"
    assert result.items[0].mock_url == "/mock/images/mock-img-P001-1.png"
    assert result.items[0].metadata["source"] == "mock"


def test_generate_image_generation_with_comfyui_provider_raises_placeholder_error() -> None:
    with pytest.raises(NotImplementedError) as exc_info:
        generate_image_generation(make_generation_input(provider="comfyui"))

    message = str(exc_info.value)
    assert "ComfyUI" in message
    assert "private deployment" in message


def test_mock_provider_does_not_call_external_services() -> None:
    result = MockImageGenerationProvider().generate(make_generation_input())

    assert result.items[0].image_url is None
    assert result.items[0].mock_url == "/mock/images/mock-img-P001-1.png"
    assert result.items[0].metadata["note"] == (
        "Mock image generation result. No real GPU or ComfyUI call was made."
    )
