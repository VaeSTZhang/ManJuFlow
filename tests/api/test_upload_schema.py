from pathlib import Path
import sys

import pytest
from pydantic import ValidationError


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.schemas.upload import (
    ScriptUploadOutput,
    UploadError,
    UploadSourceInput,
    UploadSourceMetadata,
)


def make_upload_source_metadata(**overrides) -> UploadSourceMetadata:
    data = {
        "source_id": "SRC_001",
        "project_title": "测试短剧：雨夜重逢",
        "project_id": "PROJECT_001",
        "workspace_id": "WORKSPACE_001",
        "user_id": "USER_001",
        "ai_account_id": "AI_ACCOUNT_001",
        "original_filename": "rainy-night-script.docx",
        "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "file_size": 2048,
        "sha256": "mock-sha256",
        "storage_path": "storage/user_uploads/WORKSPACE_001/SRC_001/original.docx",
        "source_type": "script_docx",
        "extraction_status": "succeeded",
        "extracted_text_length": 128,
        "created_at": "2026-05-03T10:00:00Z",
        "metadata": {"source": "mock"},
    }
    data.update(overrides)
    return UploadSourceMetadata(**data)


def make_script_upload_output(**overrides) -> ScriptUploadOutput:
    metadata = make_upload_source_metadata()
    data = {
        "source_id": metadata.source_id,
        "project_title": metadata.project_title,
        "extracted_text": "第1集 第1场｜医院门口｜雨夜。林晚和顾沉隔雨对视。",
        "metadata": metadata,
    }
    data.update(overrides)
    return ScriptUploadOutput(**data)


def test_upload_source_input_can_be_created() -> None:
    data = UploadSourceInput(project_title="测试短剧：雨夜重逢")

    assert data.project_title == "测试短剧：雨夜重逢"
    assert data.language == "zh"


def test_upload_source_input_defaults_source_type_to_script_docx() -> None:
    data = UploadSourceInput(project_title="测试短剧：雨夜重逢")

    assert data.source_type == "script_docx"


def test_upload_source_input_rejects_empty_project_title() -> None:
    with pytest.raises(ValidationError):
        UploadSourceInput(project_title="   ")


def test_upload_source_input_can_include_project_workspace_user_and_ai_account() -> None:
    data = UploadSourceInput(
        project_title="测试短剧：雨夜重逢",
        project_id="PROJECT_001",
        workspace_id="WORKSPACE_001",
        user_id="USER_001",
        ai_account_id="AI_ACCOUNT_001",
    )

    assert data.project_id == "PROJECT_001"
    assert data.workspace_id == "WORKSPACE_001"
    assert data.user_id == "USER_001"
    assert data.ai_account_id == "AI_ACCOUNT_001"


def test_upload_source_metadata_can_be_created() -> None:
    metadata = make_upload_source_metadata()

    assert metadata.source_id == "SRC_001"
    assert metadata.original_filename == "rainy-night-script.docx"


def test_upload_source_metadata_rejects_negative_file_size() -> None:
    with pytest.raises(ValidationError):
        make_upload_source_metadata(file_size=-1)


def test_upload_source_metadata_rejects_negative_extracted_text_length() -> None:
    with pytest.raises(ValidationError):
        make_upload_source_metadata(extracted_text_length=-1)


def test_script_upload_output_can_be_created() -> None:
    output = make_script_upload_output()

    assert output.source_id == "SRC_001"
    assert output.metadata.source_id == "SRC_001"


def test_script_upload_output_rejects_empty_extracted_text() -> None:
    with pytest.raises(ValidationError):
        make_script_upload_output(extracted_text="   ")


def test_script_upload_output_defaults_warnings_to_empty_list() -> None:
    output = make_script_upload_output()

    assert output.warnings == []


def test_upload_error_can_be_created() -> None:
    error = UploadError(
        error_code="unsupported_file_type",
        message="当前仅支持 .docx 剧本文档。",
        detail="请将 .doc 文件另存为 .docx 后重新上传。",
    )

    assert error.error_code == "unsupported_file_type"
    assert error.message == "当前仅支持 .docx 剧本文档。"


def test_script_upload_output_model_dump_contains_main_fields() -> None:
    output = make_script_upload_output()
    data = output.model_dump()

    assert data["source_id"] == "SRC_001"
    assert data["project_title"] == "测试短剧：雨夜重逢"
    assert data["extracted_text"] == "第1集 第1场｜医院门口｜雨夜。林晚和顾沉隔雨对视。"
    assert data["metadata"]["source_id"] == "SRC_001"
