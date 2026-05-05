from pathlib import Path
import sys

import pytest
from pydantic import ValidationError


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.schemas.document_import import (
    DocumentImportAction,
    DocumentImportError,
    DocumentImportOutput,
    DocumentImportPreview,
    DocumentImportSource,
)


def make_import_source(**overrides) -> DocumentImportSource:
    data = {
        "filename": "sample-script.docx",
        "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "file_size_bytes": 2048,
        "source_type": "docx",
        "checksum": "sample-checksum",
    }
    data.update(overrides)
    return DocumentImportSource(**data)


def make_import_preview(**overrides) -> DocumentImportPreview:
    data = {
        "source": make_import_source(),
        "extracted_text": "第一章，女主回到旧书店，发现一封没有寄出的信。",
        "preview_text": "第一章，女主回到旧书店，发现一封没有寄出的信。",
        "character_count": 25,
        "paragraph_count": 1,
        "detected_title": "旧书店来信",
    }
    data.update(overrides)
    return DocumentImportPreview(**data)


def test_document_import_source_can_be_created() -> None:
    source = DocumentImportSource(
        filename="sample-script.docx",
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        file_size_bytes=2048,
    )

    assert source.filename == "sample-script.docx"
    assert source.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    assert source.file_size_bytes == 2048
    assert source.source_type == "docx"


def test_document_import_source_rejects_empty_filename() -> None:
    with pytest.raises(ValidationError):
        DocumentImportSource(filename="   ")


def test_document_import_source_rejects_negative_file_size() -> None:
    with pytest.raises(ValidationError):
        make_import_source(file_size_bytes=-1)


def test_document_import_preview_defaults_are_independent() -> None:
    first_preview = make_import_preview()
    second_preview = make_import_preview()

    first_preview.warnings.append("文本较长，已生成预览片段。")
    first_preview.metadata["source_id"] = "SRC_001"

    assert second_preview.warnings == []
    assert second_preview.metadata == {}


def test_document_import_output_contains_preview_and_model_dump() -> None:
    preview = make_import_preview()
    output = DocumentImportOutput(
        project_title="测试短剧：旧书店来信",
        preview=preview,
    )

    dumped = output.model_dump()

    assert output.status == "preview_ready"
    assert output.next_required_action == "user_confirm_import_action"
    assert dumped["project_title"] == "测试短剧：旧书店来信"
    assert dumped["preview"]["source"]["filename"] == "sample-script.docx"
    assert dumped["preview"]["extracted_text"] == "第一章，女主回到旧书店，发现一封没有寄出的信。"


def test_document_import_output_accepts_context_options() -> None:
    preview = make_import_preview()
    output = DocumentImportOutput(
        project_title="测试短剧：旧书店来信",
        preview=preview,
        context_options={
            "project_id": "project_old_bookstore",
            "session_id": "session_import_preview",
        },
    )
    dumped = output.model_dump()

    assert output.context_options is not None
    assert output.context_options.context_policy == "current_project_only"
    assert dumped["context_options"]["project_id"] == "project_old_bookstore"
    assert dumped["context_options"]["session_id"] == "session_import_preview"


def test_document_import_context_options_do_not_leak_local_paths() -> None:
    preview = make_import_preview()
    output = DocumentImportOutput(
        project_title="测试短剧：旧书店来信",
        preview=preview,
        context_options={
            "project_id": "project_old_bookstore",
            "session_id": "session_import_preview",
        },
    )
    dumped_text = str(output.model_dump())

    assert "/Users/example" not in dumped_text
    assert "server_path" not in dumped_text
    assert "local_path" not in dumped_text


def test_document_import_action_supports_fill() -> None:
    action = DocumentImportAction(
        action="fill",
        imported_text="第一章，女主回到旧书店。",
    )

    assert action.action == "fill"
    assert action.target_field == "source_text"
    assert action.imported_text == "第一章，女主回到旧书店。"


def test_document_import_action_supports_append() -> None:
    action = DocumentImportAction(
        action="append",
        target_field="source_text",
        imported_text="第二章，旧信指向一场舞台事故。",
    )

    assert action.action == "append"
    assert action.target_field == "source_text"


def test_document_import_action_supports_cancel() -> None:
    action = DocumentImportAction(action="cancel")

    assert action.action == "cancel"
    assert action.imported_text is None


def test_document_import_action_rejects_invalid_action() -> None:
    with pytest.raises(ValidationError):
        DocumentImportAction(action="replace")


def test_document_import_error_can_be_created_without_local_path() -> None:
    error = DocumentImportError(
        error_code="unsupported_file_type",
        message="当前仅支持 .docx 文档。",
        filename="sample.pdf",
        details={"max_file_size_mb": 10},
    )
    dumped = error.model_dump()

    assert error.error_code == "unsupported_file_type"
    assert error.filename == "sample.pdf"
    assert "path" not in dumped
    assert "server_path" not in dumped["details"]
