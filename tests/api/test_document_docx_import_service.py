from io import BytesIO
from pathlib import Path
import sys

import pytest
from docx import Document

API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.schemas.context import ContextOptions
from app.schemas.document_import import DocumentImportOutput
from app.services.document_import_service import (
    build_docx_import_preview,
    parse_docx_bytes_to_text,
)


def build_safe_docx_bytes(paragraphs: list[str]) -> bytes:
    document = Document()
    for paragraph in paragraphs:
        document.add_paragraph(paragraph)

    buffer = BytesIO()
    document.save(buffer)
    return buffer.getvalue()


def test_parse_docx_bytes_to_text_extracts_multiple_paragraphs() -> None:
    file_bytes = build_safe_docx_bytes(
        [
            "旧影院来信",
            "放映员收到一封来自未来的信。",
            "旧胶片在午夜重新亮起。",
        ]
    )

    text = parse_docx_bytes_to_text(file_bytes)

    assert text == "旧影院来信\n放映员收到一封来自未来的信。\n旧胶片在午夜重新亮起。"


def test_parse_docx_bytes_to_text_skips_empty_paragraphs() -> None:
    file_bytes = build_safe_docx_bytes(
        [
            "雨巷旧梦",
            "",
            "   ",
            "女主在旧桥边发现父亲留下的账本。",
        ]
    )

    text = parse_docx_bytes_to_text(file_bytes)

    assert text == "雨巷旧梦\n女主在旧桥边发现父亲留下的账本。"


def test_parse_docx_bytes_to_text_rejects_empty_bytes() -> None:
    with pytest.raises(ValueError, match="DOCX 文件内容为空"):
        parse_docx_bytes_to_text(b"")


def test_parse_docx_bytes_to_text_rejects_invalid_docx_bytes() -> None:
    with pytest.raises(ValueError, match="无法解析 DOCX 文档"):
        parse_docx_bytes_to_text(b"not a docx package")


def test_build_docx_import_preview_returns_document_import_output() -> None:
    file_bytes = build_safe_docx_bytes(
        [
            "旧影院来信",
            "放映员在拆迁前夜收到一封没有署名的信。",
            "信中提到最后一场电影会改变所有人的命运。",
        ]
    )
    context_options = ContextOptions(
        user_id="internal_user_mock_001",
        workspace_id="workspace_dramora_internal",
        project_id="project_docx_import_safe_sample",
        session_id="session_docx_import_safe_sample",
        request_id="request_docx_import_safe_sample",
        source_stage="imported_document",
    )

    output = build_docx_import_preview(
        file_bytes=file_bytes,
        filename="/Users/example/Documents/old-cinema.docx",
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        project_title="旧影院来信",
        context_options=context_options,
    )

    assert isinstance(output, DocumentImportOutput)
    assert output.project_title == "旧影院来信"
    assert output.preview.source.filename == "old-cinema.docx"
    assert output.preview.source.source_type == "docx"
    assert output.preview.source.file_size_bytes == len(file_bytes)
    assert "放映员在拆迁前夜" in output.preview.extracted_text
    assert output.preview.character_count > 0
    assert output.preview.paragraph_count == 3
    assert output.context_options is not None
    assert output.context_options.project_id == "project_docx_import_safe_sample"
    assert output.context_options.session_id == "session_docx_import_safe_sample"


def test_build_docx_import_preview_metadata_does_not_include_local_paths() -> None:
    file_bytes = build_safe_docx_bytes(["安全虚构文档", "这里只包含测试用虚构文本。"])

    output = build_docx_import_preview(
        file_bytes=file_bytes,
        filename="/Users/example/secret/source.docx",
    )
    output_dump = output.model_dump()
    output_text = str(output_dump)

    assert "source.docx" == output.preview.source.filename
    assert "server_path" not in output_text
    assert "local_path" not in output_text
    assert "absolute_path" not in output_text
    assert "/Users/example/secret" not in output_text
