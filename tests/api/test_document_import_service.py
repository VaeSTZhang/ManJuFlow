from pathlib import Path
import sys


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.schemas.document_import import DocumentImportOutput
from app.services.document_import_service import (
    DOCUMENT_IMPORT_PREVIEW_OMISSION_MARKER,
    build_document_import_preview,
    build_preview_text,
    detect_document_title,
    estimate_paragraph_count,
    normalize_imported_text,
)


def test_normalize_imported_text_unifies_line_breaks_and_strips() -> None:
    text = "  第一段\r\n第二段\r第三段  "

    normalized = normalize_imported_text(text)

    assert normalized == "第一段\n第二段\n第三段"


def test_build_preview_text_returns_short_text_unchanged() -> None:
    text = "第一章，女主回到旧书店。"

    preview = build_preview_text(text, max_chars=1000)

    assert preview == text


def test_build_preview_text_truncates_long_text_with_marker() -> None:
    text = "雨" * 1200

    preview = build_preview_text(text, max_chars=1000)

    assert len(preview) < len(text)
    assert preview.endswith(DOCUMENT_IMPORT_PREVIEW_OMISSION_MARKER)
    assert preview.startswith("雨" * 20)


def test_estimate_paragraph_count_counts_non_empty_paragraphs() -> None:
    text = "第一段\n\n  \n第二段\n第三段"

    assert estimate_paragraph_count(text) == 3
    assert estimate_paragraph_count("  \n\n") == 0


def test_detect_document_title_reads_first_non_empty_line() -> None:
    text = "\n\n旧书店来信\n第一章，女主回到旧书店。"

    title = detect_document_title(text)

    assert title == "旧书店来信"


def test_detect_document_title_uses_filename_when_text_empty() -> None:
    title = detect_document_title("", fallback_filename="/Users/example/Documents/old-bookstore.docx")

    assert title == "old-bookstore"


def test_build_document_import_preview_returns_output() -> None:
    output = build_document_import_preview(
        filename="old-bookstore.docx",
        extracted_text="旧书店来信\n第一章，女主回到旧书店。",
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        file_size_bytes=4096,
        project_title="测试短剧：旧书店来信",
        checksum="safe-checksum",
    )

    assert isinstance(output, DocumentImportOutput)
    assert output.project_title == "测试短剧：旧书店来信"
    assert output.status == "preview_ready"
    assert output.next_required_action == "user_confirm_import_action"
    assert output.preview.source.filename == "old-bookstore.docx"
    assert output.preview.source.checksum == "safe-checksum"


def test_build_document_import_preview_counts_characters_and_paragraphs() -> None:
    output = build_document_import_preview(
        filename="old-bookstore.docx",
        extracted_text="旧书店来信\n\n第一章，女主回到旧书店。\n第二章，旧信指向舞台事故。",
    )

    assert output.preview.character_count == len("旧书店来信\n\n第一章，女主回到旧书店。\n第二章，旧信指向舞台事故。")
    assert output.preview.paragraph_count == 3
    assert output.preview.detected_title == "旧书店来信"


def test_build_document_import_preview_marks_truncated_preview() -> None:
    output = build_document_import_preview(
        filename="long-novel.docx",
        extracted_text="雨" * 1200,
    )

    assert output.preview.metadata["safe_preview_truncated"] is True
    assert output.preview.preview_text.endswith(DOCUMENT_IMPORT_PREVIEW_OMISSION_MARKER)
    assert output.preview.warnings == ["文档内容较长，当前仅显示前部预览。"]


def test_build_document_import_preview_dump_has_no_local_path_fields() -> None:
    output = build_document_import_preview(
        filename="/Users/example/Documents/private-novel.docx",
        extracted_text="旧书店来信\n第一章，女主回到旧书店。",
        source_type="novel",
    )
    dumped = output.model_dump()

    assert dumped["preview"]["source"]["filename"] == "private-novel.docx"
    assert dumped["preview"]["metadata"]["source_type"] == "novel"
    assert "server_path" not in dumped
    assert "local_path" not in dumped
    assert "absolute_path" not in dumped
    assert "server_path" not in dumped["preview"]["metadata"]
    assert "local_path" not in dumped["preview"]["metadata"]
    assert "absolute_path" not in dumped["preview"]["metadata"]
