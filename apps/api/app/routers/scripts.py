from fastapi import APIRouter, HTTPException

from app.schemas.idea import IdeaInput
from app.schemas.script import ScriptOutput
from app.schemas.script_segmentation import ExistingScriptInput, ScriptSegmentationOutput
from app.services.script_service import generate_script
from app.services.script_segmentation_service import generate_script_segmentation


router = APIRouter(prefix="/api/scripts", tags=["scripts"])


@router.post("/generate", response_model=ScriptOutput)
def generate_script_endpoint(input_data: IdeaInput) -> ScriptOutput:
    try:
        return generate_script(input_data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/segment", response_model=ScriptSegmentationOutput)
def segment_script(input_data: ExistingScriptInput) -> ScriptSegmentationOutput:
    try:
        return generate_script_segmentation(input_data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
