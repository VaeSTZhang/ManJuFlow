from app.schemas.context import ContextOptions
from app.schemas.document import DocumentExportInput, DocumentExportOutput
from app.schemas.document_import import DocumentImportOutput
from app.schemas.usage_ledger import UsageLedgerCreate
from app.services.usage_ledger_service import create_usage_ledger_entry


def record_document_import_usage(
    *,
    output: DocumentImportOutput | None,
    context_options: ContextOptions | None,
    status: str = "success",
    error_code: str | None = None,
    error_message_safe: str | None = None,
    file_size_bytes: int | None = None,
    character_count: int | None = None,
    paragraph_count: int | None = None,
    has_detected_title: bool | None = None,
    source_type: str | None = None,
) -> None:
    preview = output.preview if output is not None else None
    source = preview.source if preview is not None else None
    metadata = {
        "document_operation": "import_preview",
        "file_size_bytes": file_size_bytes if file_size_bytes is not None else (source.file_size_bytes if source else None),
        "character_count": character_count if character_count is not None else (preview.character_count if preview else None),
        "paragraph_count": paragraph_count if paragraph_count is not None else (preview.paragraph_count if preview else None),
        "has_detected_title": has_detected_title if has_detected_title is not None else bool(preview.detected_title if preview else False),
        "source_type": source_type if source_type is not None else (source.source_type if source else None),
    }

    create_usage_ledger_entry(
        UsageLedgerCreate(
            operation="document_import",
            status=status,
            context=context_options,
            source_stage=(
                context_options.source_stage
                if context_options and context_options.source_stage
                else "imported_document"
            ),
            request_id=context_options.request_id if context_options else None,
            error_code=error_code,
            error_message=error_message_safe,
            metadata={key: value for key, value in metadata.items() if value is not None},
        )
    )


def record_document_export_usage(
    *,
    input_data: DocumentExportInput,
    output: DocumentExportOutput | None = None,
    document_operation: str | None = None,
    status: str = "success",
    error_code: str | None = None,
    error_message_safe: str | None = None,
    output_character_count: int | None = None,
    file_size_bytes: int | None = None,
) -> None:
    context_options = input_data.context_options
    export_format = input_data.export_format
    resolved_document_operation = document_operation or f"export_{export_format}"
    metadata = {
        "document_operation": resolved_document_operation,
        "document_type": input_data.document_type,
        "export_format": export_format,
        "source_stage": input_data.source_stage,
        "output_character_count": output_character_count if output_character_count is not None else _output_character_count(output),
        "file_size_bytes": file_size_bytes if file_size_bytes is not None else (output.file_size_bytes if output else None),
        "episode_count": _structured_count(input_data, "episodes"),
        "characters_count": _structured_count(input_data, "characters"),
    }

    create_usage_ledger_entry(
        UsageLedgerCreate(
            operation="document_export",
            status=status,
            context=context_options,
            source_stage=(
                context_options.source_stage
                if context_options and context_options.source_stage
                else input_data.source_stage
            ),
            request_id=context_options.request_id if context_options else None,
            error_code=error_code,
            error_message=error_message_safe,
            metadata={key: value for key, value in metadata.items() if value is not None},
        )
    )


def _output_character_count(output: DocumentExportOutput | None) -> int | None:
    if output is None or output.content_text is None:
        return None
    return len(output.content_text)


def _structured_count(input_data: DocumentExportInput, key: str) -> int | None:
    if input_data.structured_payload is None:
        return None
    value = input_data.structured_payload.get(key)
    if isinstance(value, list):
        return len(value)
    return None
