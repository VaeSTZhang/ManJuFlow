from fastapi import APIRouter

from app.schemas.storyboard import StoryboardInput, StoryboardOutput
from app.services.storyboard_service import generate_storyboard


router = APIRouter(prefix="/api/storyboards", tags=["storyboards"])


@router.post("/generate", response_model=StoryboardOutput)
def generate_storyboard_endpoint(input_data: StoryboardInput) -> StoryboardOutput:
    return generate_storyboard(input_data)
