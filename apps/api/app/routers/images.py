from fastapi import APIRouter

from app.schemas.image_generation import ImageGenerationInput, ImageGenerationOutput
from app.services.image_generation_service import generate_image_generation


router = APIRouter(prefix="/api/images", tags=["images"])


@router.post("/generate", response_model=ImageGenerationOutput)
def generate_image_generation_endpoint(input_data: ImageGenerationInput) -> ImageGenerationOutput:
    return generate_image_generation(input_data)
