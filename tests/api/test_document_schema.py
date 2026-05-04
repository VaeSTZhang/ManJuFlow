from pathlib import Path
import sys

import pytest
from pydantic import ValidationError


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.schemas.document import DocumentExportInput, DocumentExportOutput


def test_document_export_input_can_create_with_content_text() -> None:
    input_data = DocumentExportInput(
        project_title="测试短剧：雨夜重逢",
        content_text="第一场，雨夜医院门口。",
    )

    assert input_data.project_title == "测试短剧：雨夜重逢"
    assert input_data.content_text == "第一场，雨夜医院门口。"
    assert input_data.document_type == "creative_document"
    assert input_data.source_stage == "script"
    assert input_data.export_format == "txt"


def test_document_export_input_can_create_with_structured_payload() -> None:
    input_data = DocumentExportInput(
        project_title="测试短剧：雨夜重逢",
        structured_payload={"episodes": [{"episode_number": 1}]},
        export_format="json",
    )

    assert input_data.structured_payload == {"episodes": [{"episode_number": 1}]}
    assert input_data.export_format == "json"


@pytest.mark.parametrize("export_format", ["txt", "json", "docx"])
def test_document_export_input_supports_export_formats(export_format: str) -> None:
    input_data = DocumentExportInput(
        project_title="测试短剧：雨夜重逢",
        content_text="测试内容",
        export_format=export_format,
    )

    assert input_data.export_format == export_format


@pytest.mark.parametrize("source_stage", ["script", "storyboard", "image_prompt"])
def test_document_export_input_supports_source_stages(source_stage: str) -> None:
    input_data = DocumentExportInput(
        project_title="测试短剧：雨夜重逢",
        content_text="测试内容",
        source_stage=source_stage,
    )

    assert input_data.source_stage == source_stage


def test_document_export_input_metadata_default_is_independent_dict() -> None:
    first_input = DocumentExportInput(project_title="项目 A", content_text="内容 A")
    second_input = DocumentExportInput(project_title="项目 B", content_text="内容 B")

    first_input.metadata["source"] = "test"

    assert second_input.metadata == {}


def test_document_export_output_can_create() -> None:
    output = DocumentExportOutput(
        project_title="测试短剧：雨夜重逢",
        document_type="creative_document",
        source_stage="storyboard",
        export_format="txt",
        filename="storyboard.txt",
        content_text="分镜文本",
        file_size_bytes=128,
    )

    assert output.project_title == "测试短剧：雨夜重逢"
    assert output.document_type == "creative_document"
    assert output.source_stage == "storyboard"
    assert output.export_format == "txt"
    assert output.filename == "storyboard.txt"
    assert output.file_size_bytes == 128


def test_document_export_output_model_dump_contains_core_fields() -> None:
    output = DocumentExportOutput(
        project_title="测试短剧：雨夜重逢",
        document_type="creative_document",
        source_stage="script",
        export_format="docx",
        filename="script.docx",
    )

    dumped = output.model_dump()

    assert dumped["project_title"] == "测试短剧：雨夜重逢"
    assert dumped["filename"] == "script.docx"
    assert dumped["export_format"] == "docx"


def test_document_export_input_rejects_invalid_export_format() -> None:
    with pytest.raises(ValidationError):
        DocumentExportInput(
            project_title="测试短剧：雨夜重逢",
            content_text="测试内容",
            export_format="pdf",
        )


def test_document_export_input_rejects_invalid_source_stage() -> None:
    with pytest.raises(ValidationError):
        DocumentExportInput(
            project_title="测试短剧：雨夜重逢",
            content_text="测试内容",
            source_stage="video",
        )
