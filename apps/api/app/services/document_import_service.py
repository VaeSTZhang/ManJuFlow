from io import BytesIO
from pathlib import PurePosixPath

from docx import Document

from app.schemas.context import ContextOptions
from app.schemas.document_import import (
    DocumentImportOutput,
    DocumentImportPreview,
    DocumentImportSource,
)
from app.services.document_usage_ledger import record_document_import_usage
from app.services.ownership_service import record_import_document_ownership


DEFAULT_IMPORT_PREVIEW_MAX_CHARS = 1000
DOCUMENT_IMPORT_PREVIEW_OMISSION_MARKER = "\n\n……（后续内容已省略，仅用于预览）"
DOCUMENT_IMPORT_EMPTY_TEXT_WARNING = "未提取到可用文本，请检查文档内容。"
DOCUMENT_IMPORT_PREVIEW_TRUNCATED_WARNING = "文档内容较长，当前仅显示前部预览。"
DOCUMENT_IMPORT_FILENAME_NORMALIZED_WARNING = "文件名已做安全清洗，仅保留文件名。"
DOCUMENT_IMPORT_TITLE_MAX_CHARS = 80
DOCX_PARSE_EMPTY_FILE_ERROR = "DOCX 文件内容为空，无法解析。"
DOCX_PARSE_INVALID_FILE_ERROR = "无法解析 DOCX 文档，请确认文件格式正确。"


def _safe_filename(filename: str) -> str:
    normalized_filename = filename.replace("\\", "/").strip()
    safe_filename = PurePosixPath(normalized_filename).name.strip()
    return safe_filename or "document.docx"


def normalize_imported_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n").strip()


def build_preview_text(text: str, max_chars: int = DEFAULT_IMPORT_PREVIEW_MAX_CHARS) -> str:
    if len(text) <= max_chars:
        return text

    return f"{text[:max_chars].rstrip()}{DOCUMENT_IMPORT_PREVIEW_OMISSION_MARKER}"


def estimate_paragraph_count(text: str) -> int:
    return len([paragraph for paragraph in text.split("\n") if paragraph.strip()])


def detect_document_title(text: str, fallback_filename: str | None = None) -> str | None:
    for line in text.split("\n"):
        title = line.strip()
        if title:
            return title[:DOCUMENT_IMPORT_TITLE_MAX_CHARS]

    if fallback_filename is None:
        return None

    safe_filename = _safe_filename(fallback_filename)
    title = safe_filename.rsplit(".", 1)[0].strip()
    return title[:DOCUMENT_IMPORT_TITLE_MAX_CHARS] or None


def parse_docx_bytes_to_text(file_bytes: bytes) -> str:
    if not file_bytes:
        raise ValueError(DOCX_PARSE_EMPTY_FILE_ERROR)

    try:
        document = Document(BytesIO(file_bytes))
    except Exception as exc:
        raise ValueError(DOCX_PARSE_INVALID_FILE_ERROR) from exc

    paragraphs = [
        paragraph.text.strip()
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    ]
    return "\n".join(paragraphs).strip()


def build_document_import_preview(
    *,
    filename: str,
    extracted_text: str,
    content_type: str | None = None,
    file_size_bytes: int | None = None,
    source_type: str = "docx",
    project_title: str | None = None,
    checksum: str | None = None,
    context_options: ContextOptions | None = None,
) -> DocumentImportOutput:
    safe_filename = _safe_filename(filename)
    normalized_text = normalize_imported_text(extracted_text)
    preview_text = build_preview_text(normalized_text)
    preview_truncated = preview_text != normalized_text
    warnings = []

    if not normalized_text:
        warnings.append(DOCUMENT_IMPORT_EMPTY_TEXT_WARNING)
        preview_text = "未提取到可用文本。"

    if preview_truncated:
        warnings.append(DOCUMENT_IMPORT_PREVIEW_TRUNCATED_WARNING)

    if safe_filename != filename.strip():
        warnings.append(DOCUMENT_IMPORT_FILENAME_NORMALIZED_WARNING)

    source = DocumentImportSource(
        filename=safe_filename,
        content_type=content_type,
        file_size_bytes=file_size_bytes,
        source_type=source_type,
        checksum=checksum,
    )
    preview = DocumentImportPreview(
        source=source,
        extracted_text=normalized_text or "未提取到可用文本。",
        preview_text=preview_text,
        character_count=len(normalized_text),
        paragraph_count=estimate_paragraph_count(normalized_text),
        detected_title=detect_document_title(normalized_text, safe_filename),
        warnings=warnings,
        metadata={
            "safe_preview_truncated": preview_truncated,
            "source_type": source_type,
        },
    )

    output = DocumentImportOutput(
        project_title=project_title,
        preview=preview,
        context_options=context_options,
    )
    record_import_document_ownership(
        context_options=context_options,
        project_title=project_title or preview.detected_title,
        source_mode=source_type,
        filename_safe=safe_filename,
        content_type=content_type,
        file_size_bytes=file_size_bytes,
        character_count=preview.character_count,
        paragraph_count=preview.paragraph_count,
        source_type=source_type,
        has_detected_title=preview.detected_title is not None,
    )
    record_document_import_usage(output=output, context_options=context_options)
    return output


def build_docx_import_preview(
    *,
    file_bytes: bytes,
    filename: str,
    content_type: str | None = None,
    file_size_bytes: int | None = None,
    project_title: str | None = None,
    context_options: ContextOptions | None = None,
) -> DocumentImportOutput:
    try:
        extracted_text = parse_docx_bytes_to_text(file_bytes)
    except ValueError as exc:
        record_document_import_usage(
            output=None,
            context_options=context_options,
            status="failed",
            error_code="document_import_failed",
            error_message_safe=str(exc),
            file_size_bytes=file_size_bytes if file_size_bytes is not None else len(file_bytes),
            source_type="docx",
        )
        raise
    return build_document_import_preview(
        filename=filename,
        extracted_text=extracted_text,
        content_type=content_type,
        file_size_bytes=file_size_bytes if file_size_bytes is not None else len(file_bytes),
        source_type="docx",
        project_title=project_title,
        context_options=context_options,
    )
