from fastapi import APIRouter

from app.schemas.idea import IdeaInput
from app.schemas.script import ScriptOutput
from app.services.script_service import generate_script


router = APIRouter(prefix="/api/scripts", tags=["scripts"])


@router.post("/generate", response_model=ScriptOutput)
def generate_script_endpoint(input_data: IdeaInput) -> ScriptOutput:
    return generate_script(input_data)
