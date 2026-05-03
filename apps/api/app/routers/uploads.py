from fastapi import APIRouter

from app.schemas.upload import ScriptUploadOutput, UploadSourceInput
from app.services.upload_service import create_script_upload_mock


router = APIRouter(prefix="/api/uploads", tags=["uploads"])


@router.post("/script", response_model=ScriptUploadOutput)
def upload_script_mock(input_data: UploadSourceInput) -> ScriptUploadOutput:
    """Mock metadata-only script upload; no real file is received or saved."""
    return create_script_upload_mock(input_data)
