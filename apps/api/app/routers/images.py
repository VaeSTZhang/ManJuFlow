from fastapi import APIRouter

from app.schemas.image_generation import ImageGenerationInput, ImageGenerationOutput
from app.schemas.image_generation_bundle import ImageGenerationBundleOutput
from app.services.image_generation_bundle_service import build_image_generation_bundle
from app.services.image_generation_service import generate_image_generation


router = APIRouter(prefix="/api/images", tags=["images"])


@router.post("/generate", response_model=ImageGenerationOutput)
def generate_image_generation_endpoint(input_data: ImageGenerationInput) -> ImageGenerationOutput:
    return generate_image_generation(input_data)


@router.post("/generate-bundle", response_model=ImageGenerationBundleOutput)
def generate_image_generation_bundle_endpoint(input_data: ImageGenerationInput) -> ImageGenerationBundleOutput:
    image_generation_output = generate_image_generation(input_data)
    return build_image_generation_bundle(image_generation_output)
