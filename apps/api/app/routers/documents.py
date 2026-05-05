from fastapi import APIRouter, File, Form, HTTPException, Response, UploadFile

from app.schemas.context import ContextOptions
from app.schemas.document import DocumentExportInput, DocumentExportOutput
from app.schemas.document_import import DocumentImportOutput, DocumentImportPreviewRequest
from app.services.document_docx_export_service import build_docx_export_bytes, sanitize_docx_filename
from app.services.document_export_service import export_document
from app.services.document_import_service import build_document_import_preview, build_docx_import_preview


router = APIRouter(prefix="/api/documents", tags=["documents"])
DOCX_CONTENT_TYPES = {
    "",
    "application/octet-stream",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/zip",
    "application/x-zip-compressed",
}


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
            context_options=input_data.context_options,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/import-docx-preview", response_model=DocumentImportOutput)
async def preview_docx_document_import(
    file: UploadFile = File(...),
    project_title: str | None = Form(None),
    user_id: str | None = Form(None),
    workspace_id: str | None = Form(None),
    project_id: str | None = Form(None),
    session_id: str | None = Form(None),
    request_id: str | None = Form(None),
    source_stage: str | None = Form("imported_document"),
    context_policy: str = Form("current_project_only"),
) -> DocumentImportOutput:
    """Build a DOCX document import preview without storing the uploaded file."""
    filename = (file.filename or "").strip()
    if not filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="仅支持 .docx 文件导入预览。")

    content_type = file.content_type or ""
    if content_type not in DOCX_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="上传文件类型不是受支持的 DOCX 文档。")

    file_bytes = await file.read()
    context_options = ContextOptions(
        user_id=user_id,
        workspace_id=workspace_id,
        project_id=project_id,
        session_id=session_id,
        request_id=request_id,
        source_stage=source_stage,
        context_policy=context_policy,
    )

    try:
        return build_docx_import_preview(
            file_bytes=file_bytes,
            filename=filename,
            content_type=content_type,
            file_size_bytes=len(file_bytes),
            project_title=project_title,
            context_options=context_options,
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
