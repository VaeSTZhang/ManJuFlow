from fastapi import APIRouter, HTTPException

from app.schemas.upload import ScriptUploadOutput, UploadSourceInput
from app.services.upload_service import create_script_upload_mock


router = APIRouter(prefix="/api/uploads", tags=["uploads"])


@router.post("/script", response_model=ScriptUploadOutput)
def upload_script_mock(input_data: UploadSourceInput) -> ScriptUploadOutput:
    """Mock metadata-only script upload; no real file is received or saved."""
    try:
        return create_script_upload_mock(input_data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
