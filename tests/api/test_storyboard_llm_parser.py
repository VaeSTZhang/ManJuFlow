import json
from pathlib import Path
import sys

import pytest


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.schemas.storyboard import StoryboardOutput
from app.services.storyboard_service import parse_storyboard_llm_response


def make_storyboard_output_data() -> dict:
    return {
        "project_title": "测试短剧：雨夜重逢",
        "episode_number": 1,
        "storyboard_summary": "雨夜医院门口重逢，情绪从压抑到对峙。",
        "scenes": [
            {
                "scene_id": "S001",
                "scene_number": 1,
                "location": "医院门口",
                "time": "雨夜",
                "scene_summary": "林晚和顾沉在雨夜医院门口重逢。",
                "scene_conflict": "顾沉试图确认林晚回来的目的，林晚保持距离。",
                "shots": [
                    {
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
                ],
            }
        ],
    }


def test_parse_storyboard_llm_response_accepts_plain_json() -> None:
    raw_text = json.dumps(make_storyboard_output_data(), ensure_ascii=False)

    result = parse_storyboard_llm_response(raw_text)

    assert isinstance(result, StoryboardOutput)
    assert result.project_title == "测试短剧：雨夜重逢"
    assert result.scenes[0].scene_id == "S001"
    assert result.scenes[0].shots[0].shot_id == "S001_SH001"


def test_parse_storyboard_llm_response_accepts_json_code_fence() -> None:
    json_text = json.dumps(make_storyboard_output_data(), ensure_ascii=False)
    raw_text = f"```json\n{json_text}\n```"

    result = parse_storyboard_llm_response(raw_text)

    assert result.project_title == "测试短剧：雨夜重逢"
    assert result.scenes[0].scene_id == "S001"


def test_parse_storyboard_llm_response_rejects_empty_text() -> None:
    with pytest.raises(ValueError):
        parse_storyboard_llm_response("")


def test_parse_storyboard_llm_response_rejects_invalid_json() -> None:
    with pytest.raises(ValueError, match="Storyboard LLM response is not valid JSON"):
        parse_storyboard_llm_response("这不是 JSON")


def test_parse_storyboard_llm_response_rejects_schema_mismatch() -> None:
    invalid_data = {
        "project_title": "测试短剧：雨夜重逢",
        "episode_number": 1,
        "storyboard_summary": "雨夜医院门口重逢。",
        "scenes": [],
    }
    raw_text = json.dumps(invalid_data, ensure_ascii=False)

    with pytest.raises(ValueError, match="Storyboard LLM response does not match StoryboardOutput schema"):
        parse_storyboard_llm_response(raw_text)
