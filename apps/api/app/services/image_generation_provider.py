from typing import Protocol

from app.schemas.image_generation import ImageGenerationInput, ImageGenerationOutput


class ImageGenerationProvider(Protocol):
    """Image generation provider abstraction.

    The public repository only includes the mock provider and a ComfyUI placeholder.
    Real ComfyUI server configuration, workflow definitions, authentication, model
    paths, and deployment details must live in a private deployment environment.
    """

    def generate(self, input_data: ImageGenerationInput) -> ImageGenerationOutput:
        """Generate image results from ImageGenerationInput."""


class MockImageGenerationProvider:
    def generate(self, input_data: ImageGenerationInput) -> ImageGenerationOutput:
        from app.services.image_generation_service import generate_image_generation_mock

        return generate_image_generation_mock(input_data)


class ComfyUIImageGenerationProviderPlaceholder:
    def generate(self, input_data: ImageGenerationInput) -> ImageGenerationOutput:
        raise NotImplementedError(
            "ComfyUI image generation is not implemented in the public repository. "
            "Real ComfyUI integration must be implemented in a private deployment environment "
            "with private workflow, server, authentication, and model configuration."
        )


def get_image_generation_provider(provider_name: str) -> ImageGenerationProvider:
    normalized_provider = provider_name.strip().lower()

    if normalized_provider == "mock":
        return MockImageGenerationProvider()

    if normalized_provider == "comfyui":
        return ComfyUIImageGenerationProviderPlaceholder()

    raise ValueError(
        f"Unsupported image generation provider: {provider_name}. "
        "Supported providers are 'mock' and 'comfyui'."
    )
