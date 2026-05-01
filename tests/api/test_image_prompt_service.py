import json
from pathlib import Path
import sys

import pytest


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.config import get_settings
from app.schemas.image_prompt import ImagePromptInput, ImagePromptOutput
from app.services import image_prompt_service
from app.services.image_prompt_service import (
    generate_image_prompt,
    generate_image_prompt_llm,
    generate_image_prompt_mock,
    load_image_prompt_template,
)


@pytest.fixture(autouse=True)
def reset_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def make_image_prompt_input() -> ImagePromptInput:
    return ImagePromptInput(
        project_title="测试短剧：雨夜重逢",
        storyboard_summary="雨夜医院门口重逢，情绪从压抑到对峙。",
        storyboard_text="S001_SH001 雨夜医院门口，林晚撑着黑伞站在台阶边，顾沉从车里下来，两人在雨幕和冷色车灯中对视。",
        target_model="general",
        aspect_ratio="9:16",
        style_preset="cinematic realistic",
    )


def make_image_prompt_input_with_request_model() -> ImagePromptInput:
    return ImagePromptInput(
        project_title="测试短剧：雨夜重逢",
        storyboard_summary="雨夜医院门口重逢，情绪从压抑到对峙。",
        storyboard_text="S001_SH001 雨夜医院门口，林晚撑着黑伞站在台阶边，顾沉从车里下来，两人在雨幕和冷色车灯中对视。",
        target_model="general",
        aspect_ratio="9:16",
        style_preset="cinematic realistic",
        llm_provider="kimi",
        llm_model="kimi-k2.5",
    )


def patch_image_prompt_generation_mode(monkeypatch, mode: str) -> None:
    class FakeSettings:
        image_prompt_generation_mode = mode

    monkeypatch.setattr(image_prompt_service, "get_settings", lambda: FakeSettings())


def set_image_prompt_generation_mode(monkeypatch, mode: str) -> None:
    monkeypatch.setenv("IMAGE_PROMPT_GENERATION_MODE", mode)
    get_settings.cache_clear()


def make_image_prompt_output_data() -> dict:
    return {
        "project_title": "测试短剧：雨夜重逢",
        "prompt_summary": "根据分镜生成绘图 Prompt。",
        "target_model": "general",
        "aspect_ratio": "9:16",
        "style_preset": "cinematic realistic",
        "items": [
            {
                "prompt_id": "P001",
                "shot_id": "S001_SH001",
                "scene_id": "S001",
                "shot_number": 1,
                "scene_number": 1,
                "source_visual_description": "雨夜医院门口，两人隔雨对视。",
                "positive_prompt": (
                    "cinematic realistic rainy night hospital entrance, "
                    "two characters staring through rain"
                ),
                "negative_prompt": (
                    "low quality, blurry, bad anatomy, extra fingers, distorted face, "
                    "watermark, text, logo"
                ),
                "style_preset": "cinematic realistic",
                "aspect_ratio": "9:16",
                "camera_language": "medium shot, eye-level angle",
                "lighting": "cold rainy night light",
                "color_palette": "blue gray",
                "character_consistency": "keep both characters consistent",
                "environment": "hospital entrance in heavy rain",
                "composition": "vertical frame, two characters separated by rain",
                "model_hint": "general image model",
                "seed": None,
                "notes": "test item",
            }
        ],
    }


def test_load_image_prompt_template_reads_prompt_file() -> None:
    template = load_image_prompt_template()

    assert "ImagePromptOutput" in template
    assert "positive_prompt" in template


def test_generate_image_prompt_mock_returns_output_schema() -> None:
    result = generate_image_prompt_mock(make_image_prompt_input())

    assert isinstance(result, ImagePromptOutput)


def test_generate_image_prompt_mock_keeps_project_title() -> None:
    input_data = make_image_prompt_input()

    result = generate_image_prompt_mock(input_data)

    assert result.project_title == input_data.project_title


def test_generate_image_prompt_mock_contains_multiple_items() -> None:
    result = generate_image_prompt_mock(make_image_prompt_input())

    assert len(result.items) >= 2


def test_generate_image_prompt_mock_items_have_required_prompt_fields() -> None:
    result = generate_image_prompt_mock(make_image_prompt_input())

    for item in result.items:
        assert item.positive_prompt
        assert item.negative_prompt
        assert item.shot_id
        assert item.prompt_id


def test_generate_image_prompt_mock_negative_prompt_contains_common_terms() -> None:
    result = generate_image_prompt_mock(make_image_prompt_input())

    for item in result.items:
        assert "low quality" in item.negative_prompt
        assert "blurry" in item.negative_prompt
        assert "watermark" in item.negative_prompt


def test_generate_image_prompt_returns_mock_output(monkeypatch) -> None:
    set_image_prompt_generation_mode(monkeypatch, "mock")

    result = generate_image_prompt(make_image_prompt_input())

    assert isinstance(result, ImagePromptOutput)
    assert result.project_title == "测试短剧：雨夜重逢"
    assert len(result.items) >= 2


def test_generate_image_prompt_mock_mode_ignores_request_level_llm_fields(monkeypatch) -> None:
    set_image_prompt_generation_mode(monkeypatch, "mock")

    result = generate_image_prompt(make_image_prompt_input_with_request_model())

    assert isinstance(result, ImagePromptOutput)
    assert result.project_title == "测试短剧：雨夜重逢"
    assert len(result.items) >= 2


def test_generate_image_prompt_uses_mock_mode(monkeypatch) -> None:
    patch_image_prompt_generation_mode(monkeypatch, "mock")

    result = generate_image_prompt(make_image_prompt_input())

    assert isinstance(result, ImagePromptOutput)
    assert result.project_title == "测试短剧：雨夜重逢"
    assert len(result.items) >= 2


def test_generate_image_prompt_llm_mode_uses_llm_client(monkeypatch) -> None:
    patch_image_prompt_generation_mode(monkeypatch, "llm")
    returned_messages = []

    class FakeLLMClient:
        def __init__(self, provider=None, model=None):
            self.provider = provider
            self.model = model

        def chat(self, messages):
            returned_messages.extend(messages)
            return json.dumps(make_image_prompt_output_data(), ensure_ascii=False)

    monkeypatch.setattr(image_prompt_service, "LLMClient", FakeLLMClient)

    result = generate_image_prompt(make_image_prompt_input())

    assert isinstance(result, ImagePromptOutput)
    assert returned_messages
    assert returned_messages[0]["role"] == "system"
    assert returned_messages[1]["role"] == "user"
    assert "测试短剧：雨夜重逢" in returned_messages[1]["content"]
    assert result.project_title == "测试短剧：雨夜重逢"
    assert result.items[0].prompt_id == "P001"
    assert result.items[0].shot_id == "S001_SH001"


def test_generate_image_prompt_rejects_invalid_mode(monkeypatch) -> None:
    patch_image_prompt_generation_mode(monkeypatch, "invalid")

    try:
        generate_image_prompt(make_image_prompt_input())
    except ValueError as exc:
        message = str(exc)
        assert "IMAGE_PROMPT_GENERATION_MODE" in message
        assert "mock" in message
        assert "llm" in message
    else:
        raise AssertionError("generate_image_prompt should reject invalid image prompt generation mode.")


def test_generate_image_prompt_llm_calls_parser(monkeypatch) -> None:
    raw_response = json.dumps(make_image_prompt_output_data(), ensure_ascii=False)
    parsed_payloads = []

    class FakeLLMClient:
        def __init__(self, provider=None, model=None):
            self.provider = provider
            self.model = model

        def chat(self, messages):
            return raw_response

    def fake_parse_image_prompt_llm_response(raw_text: str) -> ImagePromptOutput:
        parsed_payloads.append(raw_text)
        return ImagePromptOutput.model_validate(make_image_prompt_output_data())

    monkeypatch.setattr(image_prompt_service, "LLMClient", FakeLLMClient)
    monkeypatch.setattr(
        image_prompt_service,
        "parse_image_prompt_llm_response",
        fake_parse_image_prompt_llm_response,
    )

    result = generate_image_prompt_llm(make_image_prompt_input())

    assert isinstance(result, ImagePromptOutput)
    assert parsed_payloads == [raw_response]
    assert result.items[0].prompt_id == "P001"


def test_generate_image_prompt_llm_passes_request_level_provider_and_model(monkeypatch) -> None:
    raw_response = json.dumps(make_image_prompt_output_data(), ensure_ascii=False)
    captured_clients = []

    class FakeLLMClient:
        def __init__(self, provider=None, model=None):
            self.provider = provider
            self.model = model
            captured_clients.append(self)

        def chat(self, messages):
            return raw_response

    monkeypatch.setattr(image_prompt_service, "LLMClient", FakeLLMClient)

    result = generate_image_prompt_llm(make_image_prompt_input_with_request_model())

    assert isinstance(result, ImagePromptOutput)
    assert len(captured_clients) == 1
    assert captured_clients[0].provider == "kimi"
    assert captured_clients[0].model == "kimi-k2.5"
    assert result.items[0].prompt_id == "P001"
