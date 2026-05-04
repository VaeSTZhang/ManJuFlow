import json
import re
from pathlib import PurePosixPath
from typing import Any

from app.schemas.document import DocumentExportInput, DocumentExportOutput


DOCX_EXPORT_NOT_IMPLEMENTED_MESSAGE = "DOCX export is not implemented yet."
DEFAULT_EXPORT_BASENAME = "dramora-document"
PATH_LIKE_METADATA_KEYS = {"server_path", "local_path", "absolute_path"}


def _safe_filename_part(value: str) -> str:
    cleaned = re.sub(r"[^\w\u4e00-\u9fff.-]+", "-", value.strip(), flags=re.UNICODE)
    cleaned = cleaned.strip(".-")
    return cleaned or DEFAULT_EXPORT_BASENAME


def _strip_export_extension(filename: str) -> str:
    return filename.rsplit(".", 1)[0] if "." in filename else filename


def build_safe_export_filename(input_data: DocumentExportInput) -> str:
    export_format = input_data.export_format

    if input_data.filename:
        normalized_filename = input_data.filename.replace("\\", "/").strip()
        safe_name = PurePosixPath(normalized_filename).name.strip()
        base_name = _strip_export_extension(safe_name)
    else:
        base_name = input_data.project_title

    safe_base_name = _safe_filename_part(base_name)
    return f"{safe_base_name}.{export_format}"


def _format_structured_value(value: Any, indent: int = 0) -> list[str]:
    prefix = "  " * indent

    if isinstance(value, dict):
        lines: list[str] = []
        for key, item in value.items():
            if isinstance(item, dict | list):
                lines.append(f"{prefix}{key}:")
                lines.extend(_format_structured_value(item, indent + 1))
            else:
                lines.append(f"{prefix}{key}: {item}")
        return lines

    if isinstance(value, list):
        lines = []
        for item in value:
            if isinstance(item, dict):
                lines.append(f"{prefix}-")
                lines.extend(_format_structured_value(item, indent + 1))
            elif isinstance(item, list):
                lines.append(f"{prefix}-")
                lines.extend(_format_structured_value(item, indent + 1))
            else:
                lines.append(f"{prefix}- {item}")
        return lines

    return [f"{prefix}{value}"]


def build_txt_export_content(input_data: DocumentExportInput) -> str:
    if input_data.content_text and input_data.content_text.strip():
        body = input_data.content_text.strip()
    elif input_data.structured_payload:
        body = "\n".join(_format_structured_value(input_data.structured_payload))
    else:
        body = "无可导出内容。"

    return "\n".join(
        [
            input_data.project_title,
            "",
            body,
        ]
    )


def _sanitize_json_payload(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _sanitize_json_payload(item)
            for key, item in value.items()
            if key not in PATH_LIKE_METADATA_KEYS
        }

    if isinstance(value, list):
        return [_sanitize_json_payload(item) for item in value]

    return value


def build_json_export_content(input_data: DocumentExportInput) -> str:
    if input_data.structured_payload is not None:
        payload = _sanitize_json_payload(input_data.structured_payload)
    else:
        payload = {
            "project_title": input_data.project_title,
            "document_type": input_data.document_type,
            "source_stage": input_data.source_stage,
            "content_text": input_data.content_text or "",
        }

    return json.dumps(payload, ensure_ascii=False, indent=2)


def _build_export_metadata(input_data: DocumentExportInput, content_source: str) -> dict[str, Any]:
    metadata = {
        key: value
        for key, value in input_data.metadata.items()
        if key not in PATH_LIKE_METADATA_KEYS
    }
    metadata.update(
        {
            "export_format": input_data.export_format,
            "source_stage": input_data.source_stage,
            "document_type": input_data.document_type,
            "content_source": content_source,
        }
    )
    return metadata


def export_document(input_data: DocumentExportInput) -> DocumentExportOutput:
    if input_data.export_format == "docx":
        raise ValueError(DOCX_EXPORT_NOT_IMPLEMENTED_MESSAGE)

    if input_data.export_format == "txt":
        content_text = build_txt_export_content(input_data)
        content_source = "content_text" if input_data.content_text else "structured_payload"
    elif input_data.export_format == "json":
        content_text = build_json_export_content(input_data)
        content_source = "structured_payload" if input_data.structured_payload is not None else "content_text"
    else:
        raise ValueError(f"Unsupported export format: {input_data.export_format}")

    return DocumentExportOutput(
        project_title=input_data.project_title,
        document_type=input_data.document_type,
        source_stage=input_data.source_stage,
        export_format=input_data.export_format,
        filename=build_safe_export_filename(input_data),
        content_text=content_text,
        download_url=None,
        file_size_bytes=len(content_text.encode("utf-8")),
        workspace_id=input_data.workspace_id,
        project_id=input_data.project_id,
        session_id=input_data.session_id,
        metadata=_build_export_metadata(input_data, content_source),
    )
