from pathlib import Path
import sys


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.schemas.image_prompt import ImagePromptInput, ImagePromptOutput
from app.services.image_prompt_service import (
    generate_image_prompt,
    generate_image_prompt_mock,
    load_image_prompt_template,
)


def make_image_prompt_input() -> ImagePromptInput:
    return ImagePromptInput(
        project_title="测试短剧：雨夜重逢",
        storyboard_summary="雨夜医院门口重逢，情绪从压抑到对峙。",
        storyboard_text="S001_SH001 雨夜医院门口，林晚撑着黑伞站在台阶边，顾沉从车里下来，两人在雨幕和冷色车灯中对视。",
        target_model="general",
        aspect_ratio="9:16",
        style_preset="cinematic realistic",
    )


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


def test_generate_image_prompt_returns_mock_output() -> None:
    result = generate_image_prompt(make_image_prompt_input())

    assert isinstance(result, ImagePromptOutput)
    assert result.project_title == "测试短剧：雨夜重逢"
    assert len(result.items) >= 2
