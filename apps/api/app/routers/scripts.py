from fastapi import APIRouter

from app.schemas.idea import IdeaInput
from app.schemas.script import ScriptOutput
from app.schemas.script_segmentation import ExistingScriptInput, ScriptSegmentationOutput
from app.services.script_service import generate_script
from app.services.script_segmentation_service import generate_script_segmentation


router = APIRouter(prefix="/api/scripts", tags=["scripts"])


@router.post("/generate", response_model=ScriptOutput)
def generate_script_endpoint(input_data: IdeaInput) -> ScriptOutput:
    return generate_script(input_data)


@router.post("/segment", response_model=ScriptSegmentationOutput)
def segment_script(input_data: ExistingScriptInput) -> ScriptSegmentationOutput:
    return generate_script_segmentation(input_data)
