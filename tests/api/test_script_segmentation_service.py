from pathlib import Path
import sys


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.schemas.script_segmentation import ExistingScriptInput, ScriptSegmentationOutput
from app.services.script_segmentation_service import (
    generate_script_segmentation,
    generate_script_segmentation_mock,
)


def make_existing_script_input(**overrides) -> ExistingScriptInput:
    data = {
        "project_title": "测试短剧：雨夜重逢",
        "script_text": "第1场，雨夜医院门口。林晚撑着黑伞站在台阶下，顾沉从黑色轿车中下来，两人隔着雨幕对视。",
        "source_id": "SRC_001",
        "workspace_id": "WS_SCRIPT_SEG_001",
        "user_id": "USER_001",
        "ai_account_id": "AI_ACC_001",
    }
    data.update(overrides)
    return ExistingScriptInput(**data)


def test_generate_script_segmentation_mock_returns_output_schema() -> None:
    result = generate_script_segmentation_mock(make_existing_script_input())

    assert isinstance(result, ScriptSegmentationOutput)


def test_generate_script_segmentation_mock_keeps_project_title() -> None:
    input_data = make_existing_script_input()

    result = generate_script_segmentation_mock(input_data)

    assert result.project_title == input_data.project_title


def test_generate_script_segmentation_mock_keeps_context_identifiers() -> None:
    input_data = make_existing_script_input()

    result = generate_script_segmentation_mock(input_data)

    assert result.source_id == input_data.source_id
    assert result.workspace_id == input_data.workspace_id
    assert result.user_id == input_data.user_id
    assert result.ai_account_id == input_data.ai_account_id


def test_generate_script_segmentation_mock_segment_count_matches_segments() -> None:
    result = generate_script_segmentation_mock(make_existing_script_input())

    assert result.segment_count == len(result.segments)


def test_generate_script_segmentation_mock_creates_at_least_two_segments() -> None:
    result = generate_script_segmentation_mock(make_existing_script_input())

    assert len(result.segments) >= 2


def test_generate_script_segmentation_mock_segments_include_required_fields() -> None:
    result = generate_script_segmentation_mock(make_existing_script_input())

    for segment in result.segments:
        assert segment.segment_id
        assert segment.title
        assert segment.original_text
        assert segment.summary


def test_generate_script_segmentation_mock_segment_metadata_contains_context_policy() -> None:
    result = generate_script_segmentation_mock(make_existing_script_input())

    for segment in result.segments:
        assert segment.metadata["project_context_policy"] == "current_project_only"


def test_generate_script_segmentation_mock_metadata_generation_mode_is_mock() -> None:
    result = generate_script_segmentation_mock(make_existing_script_input())

    assert result.metadata["generation_mode"] == "mock"


def test_generate_script_segmentation_mock_supports_source_id_without_script_text() -> None:
    result = generate_script_segmentation_mock(
        make_existing_script_input(script_text=None, source_id="UPLOAD_SRC_001")
    )

    assert result.source_id == "UPLOAD_SRC_001"
    assert result.segments[0].original_text.startswith("Mock extracted text from upload source: UPLOAD_SRC_001")


def test_generate_script_segmentation_currently_returns_mock_output() -> None:
    result = generate_script_segmentation(make_existing_script_input())

    assert isinstance(result, ScriptSegmentationOutput)
    assert result.metadata["generation_mode"] == "mock"
    assert result.segment_count == len(result.segments)
