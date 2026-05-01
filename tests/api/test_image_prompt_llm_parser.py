import json
from pathlib import Path
import sys

import pytest


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.schemas.image_prompt import ImagePromptOutput
from app.services.image_prompt_service import parse_image_prompt_llm_response


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


def test_parse_image_prompt_llm_response_accepts_plain_json() -> None:
    raw_text = json.dumps(make_image_prompt_output_data(), ensure_ascii=False)

    result = parse_image_prompt_llm_response(raw_text)

    assert isinstance(result, ImagePromptOutput)
    assert result.project_title == "测试短剧：雨夜重逢"
    assert result.prompt_summary == "根据分镜生成绘图 Prompt。"
    assert result.items[0].prompt_id == "P001"
    assert result.items[0].shot_id == "S001_SH001"


def test_parse_image_prompt_llm_response_accepts_json_code_fence() -> None:
    json_text = json.dumps(make_image_prompt_output_data(), ensure_ascii=False)
    raw_text = f"```json\n{json_text}\n```"

    result = parse_image_prompt_llm_response(raw_text)

    assert result.project_title == "测试短剧：雨夜重逢"
    assert result.items[0].prompt_id == "P001"


def test_parse_image_prompt_llm_response_extracts_json_from_surrounding_text() -> None:
    json_text = json.dumps(make_image_prompt_output_data(), ensure_ascii=False)
    raw_text = f"下面是生成结果：\n{json_text}\n以上 JSON 可用于绘图。"

    result = parse_image_prompt_llm_response(raw_text)

    assert result.prompt_summary == "根据分镜生成绘图 Prompt。"
    assert result.items[0].shot_id == "S001_SH001"


def test_parse_image_prompt_llm_response_cleans_abnormal_chinese_spacing() -> None:
    data = make_image_prompt_output_data()
    data["prompt_summary"] = "根据雨夜医院 门口分镜，生成绘图 Prompt。"
    data["items"][0]["lighting"] = "保持 冷色车灯与雨夜氛围。"
    data["items"][0]["color_palette"] = "蓝灰 色主调。"
    data["items"][0]["environment"] = "雨夜医院 门口。"
    data["items"][0]["notes"] = "保持 冷色车灯。"

    raw_text = json.dumps(data, ensure_ascii=False)

    result = parse_image_prompt_llm_response(raw_text)

    assert "医院 门口" not in result.prompt_summary
    assert "保持 冷色" not in result.items[0].lighting
    assert "蓝灰 色" not in result.items[0].color_palette
    assert "医院 门口" not in result.items[0].environment
    assert "保持 冷色" not in result.items[0].notes
    assert "医院门口" in result.prompt_summary
    assert "保持冷色" in result.items[0].lighting
    assert "蓝灰色" in result.items[0].color_palette


def test_parse_image_prompt_llm_response_rejects_empty_text() -> None:
    with pytest.raises(ValueError, match="ImagePrompt LLM response is empty"):
        parse_image_prompt_llm_response("   ")


def test_parse_image_prompt_llm_response_rejects_invalid_json() -> None:
    with pytest.raises(ValueError, match="ImagePrompt LLM response is not valid JSON"):
        parse_image_prompt_llm_response("这不是 JSON")


def test_parse_image_prompt_llm_response_rejects_missing_required_field() -> None:
    data = make_image_prompt_output_data()
    data.pop("prompt_summary")

    with pytest.raises(ValueError, match="ImagePrompt LLM response does not match ImagePromptOutput schema"):
        parse_image_prompt_llm_response(json.dumps(data, ensure_ascii=False))


def test_parse_image_prompt_llm_response_rejects_empty_items() -> None:
    data = make_image_prompt_output_data()
    data["items"] = []

    with pytest.raises(ValueError, match="ImagePrompt LLM response does not match ImagePromptOutput schema"):
        parse_image_prompt_llm_response(json.dumps(data, ensure_ascii=False))


def test_parse_image_prompt_llm_response_rejects_missing_positive_prompt() -> None:
    data = make_image_prompt_output_data()
    data["items"][0].pop("positive_prompt")

    with pytest.raises(ValueError, match="ImagePrompt LLM response does not match ImagePromptOutput schema"):
        parse_image_prompt_llm_response(json.dumps(data, ensure_ascii=False))


def test_parse_image_prompt_llm_response_rejects_missing_negative_prompt() -> None:
    data = make_image_prompt_output_data()
    data["items"][0].pop("negative_prompt")

    with pytest.raises(ValueError, match="ImagePrompt LLM response does not match ImagePromptOutput schema"):
        parse_image_prompt_llm_response(json.dumps(data, ensure_ascii=False))
