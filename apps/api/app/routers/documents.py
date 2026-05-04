from fastapi import APIRouter, HTTPException, Response

from app.schemas.document import DocumentExportInput, DocumentExportOutput
from app.schemas.document_import import DocumentImportOutput, DocumentImportPreviewRequest
from app.services.document_docx_export_service import build_docx_export_bytes, sanitize_docx_filename
from app.services.document_export_service import export_document
from app.services.document_import_service import build_document_import_preview


router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/import-preview", response_model=DocumentImportOutput)
def preview_document_import(input_data: DocumentImportPreviewRequest) -> DocumentImportOutput:
    """Build a JSON-based document import preview without receiving or storing a file."""
    try:
        return build_document_import_preview(
            filename=input_data.filename,
            extracted_text=input_data.extracted_text,
            content_type=input_data.content_type,
            file_size_bytes=input_data.file_size_bytes,
            source_type=input_data.source_type,
            project_title=input_data.project_title,
            checksum=input_data.checksum,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/export", response_model=DocumentExportOutput)
def export_document_preview(input_data: DocumentExportInput) -> DocumentExportOutput:
    """Export a document payload as an in-memory TXT or JSON response."""
    try:
        return export_document(input_data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/export-file")
def export_document_file(input_data: DocumentExportInput) -> Response:
    """Export a document payload as downloadable file bytes."""
    try:
        docx_bytes = build_docx_export_bytes(input_data)
        filename = sanitize_docx_filename(input_data.filename, input_data.project_title)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
