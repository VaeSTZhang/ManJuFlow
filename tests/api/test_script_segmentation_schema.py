from pathlib import Path
import sys

import pytest
from pydantic import ValidationError


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.schemas.script_segmentation import (
    ExistingScriptInput,
    ScriptSegment,
    ScriptSegmentationOutput,
)


def make_script_segment(**overrides) -> ScriptSegment:
    data = {
        "segment_id": "SEG_001",
        "episode_number": 1,
        "scene_number": 1,
        "title": "雨夜医院门口重逢",
        "original_text": "雨夜，林晚站在医院门口，顾沉从车里下来。",
        "summary": "男女主在医院门口雨夜重逢并发生情绪冲突。",
        "characters": ["林晚", "顾沉"],
        "location": "医院门口",
        "time_of_day": "雨夜",
        "conflict": "林晚不愿说明回来原因，顾沉追问。",
        "emotion": "克制、紧张、旧情未了",
        "visual_notes": "冷色雨夜，车灯切开雨幕。",
        "dialogue_text": "顾沉：你终于肯回来了？林晚：我回来，不是为了见你。",
        "estimated_duration_seconds": 30.0,
        "next_step_hint": "可进入 Storyboard 阶段生成镜头拆解。",
        "metadata": {"source": "mock"},
    }
    data.update(overrides)
    return ScriptSegment(**data)


def test_existing_script_input_can_be_created_with_script_text() -> None:
    data = ExistingScriptInput(
        project_title="测试短剧：雨夜重逢",
        script_text="第1场。雨夜医院门口重逢。",
    )

    assert data.project_title == "测试短剧：雨夜重逢"
    assert data.script_text == "第1场。雨夜医院门口重逢。"


def test_existing_script_input_can_be_created_with_source_id() -> None:
    data = ExistingScriptInput(
        project_title="测试短剧：雨夜重逢",
        source_id="SRC_001",
        source_type="uploaded_file",
    )

    assert data.source_id == "SRC_001"
    assert data.source_type == "uploaded_file"


def test_existing_script_input_rejects_missing_script_text_and_source_id() -> None:
    with pytest.raises(ValidationError):
        ExistingScriptInput(project_title="测试短剧：雨夜重逢")


def test_existing_script_input_rejects_empty_script_text() -> None:
    with pytest.raises(ValidationError):
        ExistingScriptInput(project_title="测试短剧：雨夜重逢", script_text="   ")


def test_existing_script_input_defaults_source_type_to_pasted_text() -> None:
    data = ExistingScriptInput(project_title="测试短剧：雨夜重逢", script_text="已有剧本文本。")

    assert data.source_type == "pasted_text"


def test_existing_script_input_defaults_target_segment_level_to_scene() -> None:
    data = ExistingScriptInput(project_title="测试短剧：雨夜重逢", script_text="已有剧本文本。")

    assert data.target_segment_level == "scene"


def test_existing_script_input_can_include_workspace_user_and_ai_account() -> None:
    data = ExistingScriptInput(
        project_title="测试短剧：雨夜重逢",
        script_text="已有剧本文本。",
        workspace_id="WS_001",
        user_id="USER_001",
        ai_account_id="AI_ACC_001",
    )

    assert data.workspace_id == "WS_001"
    assert data.user_id == "USER_001"
    assert data.ai_account_id == "AI_ACC_001"


def test_script_segment_can_be_created() -> None:
    segment = make_script_segment()

    assert segment.segment_id == "SEG_001"
    assert segment.title == "雨夜医院门口重逢"
    assert segment.characters == ["林晚", "顾沉"]


def test_script_segment_rejects_negative_estimated_duration_seconds() -> None:
    with pytest.raises(ValidationError):
        make_script_segment(estimated_duration_seconds=-1)


def test_script_segmentation_output_can_include_multiple_segments() -> None:
    output = ScriptSegmentationOutput(
        project_title="测试短剧：雨夜重逢",
        segmentation_summary="已按场景切分为 2 个片段。",
        segment_count=2,
        segments=[
            make_script_segment(segment_id="SEG_001", scene_number=1),
            make_script_segment(segment_id="SEG_002", scene_number=2, title="车灯下的对峙"),
        ],
    )

    assert len(output.segments) == 2
    assert output.segment_count == 2


def test_script_segmentation_output_model_dump_contains_main_fields() -> None:
    output = ScriptSegmentationOutput(
        project_title="测试短剧：雨夜重逢",
        segmentation_summary="已按场景切分为 1 个片段。",
        segment_count=1,
        segments=[make_script_segment()],
    )

    data = output.model_dump()

    assert data["project_title"] == "测试短剧：雨夜重逢"
    assert data["segmentation_summary"] == "已按场景切分为 1 个片段。"
    assert data["segment_count"] == 1
    assert len(data["segments"]) == 1


def test_script_segmentation_output_rejects_missing_segments() -> None:
    with pytest.raises(ValidationError):
        ScriptSegmentationOutput(
            project_title="测试短剧：雨夜重逢",
            segmentation_summary="缺少片段。",
            segment_count=1,
        )


def test_script_segmentation_output_rejects_empty_segments() -> None:
    with pytest.raises(ValidationError):
        ScriptSegmentationOutput(
            project_title="测试短剧：雨夜重逢",
            segmentation_summary="缺少片段。",
            segment_count=0,
            segments=[],
        )
