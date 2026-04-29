from fastapi import APIRouter

from app.schemas.image_prompt import ImagePromptInput, ImagePromptOutput
from app.services.image_prompt_service import generate_image_prompt


router = APIRouter(prefix="/api/prompts", tags=["prompts"])


@router.post("/generate", response_model=ImagePromptOutput)
def generate_image_prompts_endpoint(input_data: ImagePromptInput) -> ImagePromptOutput:
    return generate_image_prompt(input_data)
