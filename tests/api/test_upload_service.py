from pathlib import Path
import sys


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.schemas.upload import ScriptUploadOutput, UploadSourceInput
from app.services.upload_service import (
    DOCX_UPLOAD_WARNING,
    create_script_upload_mock,
    extract_script_text_mock,
    generate_mock_source_id,
)


def make_upload_source_input(**overrides) -> UploadSourceInput:
    data = {
        "project_title": "测试短剧：雨夜重逢",
        "source_type": "script_docx",
        "project_id": "PROJECT_001",
        "workspace_id": "WORKSPACE_001",
        "user_id": "USER_001",
        "ai_account_id": "AI_ACCOUNT_001",
        "language": "zh",
    }
    data.update(overrides)
    return UploadSourceInput(**data)


def test_generate_mock_source_id_returns_prefixed_string() -> None:
    source_id = generate_mock_source_id("测试短剧：雨夜重逢", "rainy-night-script.docx")

    assert source_id.startswith("mock_upload_")


def test_generate_mock_source_id_is_stable_for_same_project_and_filename() -> None:
    first_id = generate_mock_source_id("测试短剧：雨夜重逢", "rainy-night-script.docx")
    second_id = generate_mock_source_id("测试短剧：雨夜重逢", "rainy-night-script.docx")

    assert first_id == second_id


def test_extract_script_text_mock_returns_non_empty_text() -> None:
    extracted_text = extract_script_text_mock("rainy-night-script.docx")

    assert extracted_text.strip() != ""
    assert "Mock extracted script text" in extracted_text


def test_create_script_upload_mock_returns_script_upload_output() -> None:
    output = create_script_upload_mock(make_upload_source_input())

    assert isinstance(output, ScriptUploadOutput)


def test_create_script_upload_mock_keeps_project_title() -> None:
    output = create_script_upload_mock(make_upload_source_input())

    assert output.project_title == "测试短剧：雨夜重逢"


def test_create_script_upload_mock_returns_non_empty_source_id() -> None:
    output = create_script_upload_mock(make_upload_source_input())

    assert output.source_id.startswith("mock_upload_")


def test_create_script_upload_mock_returns_non_empty_extracted_text() -> None:
    output = create_script_upload_mock(make_upload_source_input())

    assert output.extracted_text.strip() != ""


def test_create_script_upload_mock_keeps_context_fields() -> None:
    output = create_script_upload_mock(make_upload_source_input())

    assert output.metadata.project_id == "PROJECT_001"
    assert output.metadata.workspace_id == "WORKSPACE_001"
    assert output.metadata.user_id == "USER_001"
    assert output.metadata.ai_account_id == "AI_ACCOUNT_001"


def test_create_script_upload_mock_sets_extraction_status_succeeded() -> None:
    output = create_script_upload_mock(make_upload_source_input())

    assert output.metadata.extraction_status == "succeeded"


def test_create_script_upload_mock_sets_extracted_text_length() -> None:
    output = create_script_upload_mock(make_upload_source_input())

    assert output.metadata.extracted_text_length == len(output.extracted_text)


def test_create_script_upload_mock_keeps_storage_path_empty() -> None:
    output = create_script_upload_mock(make_upload_source_input())

    assert output.metadata.storage_path is None


def test_create_script_upload_mock_marks_generation_mode_as_mock() -> None:
    output = create_script_upload_mock(make_upload_source_input())

    assert output.metadata.metadata["generation_mode"] == "mock"


def test_create_script_upload_mock_has_no_warnings_for_docx_file() -> None:
    output = create_script_upload_mock(
        make_upload_source_input(),
        original_filename="rainy-night-script.docx",
    )

    assert output.warnings == []


def test_create_script_upload_mock_warns_for_non_docx_file() -> None:
    output = create_script_upload_mock(
        make_upload_source_input(),
        original_filename="rainy-night-script.txt",
        content_type="text/plain",
    )

    assert DOCX_UPLOAD_WARNING in output.warnings
