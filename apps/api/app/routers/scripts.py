from fastapi import APIRouter

from app.schemas.idea import IdeaInput
from app.schemas.script import ScriptOutput
from app.services.script_service import generate_script_mock


router = APIRouter(prefix="/api/scripts", tags=["scripts"])


@router.post("/generate", response_model=ScriptOutput)
def generate_script(input_data: IdeaInput) -> ScriptOutput:
    return generate_script_mock(input_data)
