from app.schemas.image_generation import (
    ImageGenerationInput,
    ImageGenerationItem,
    ImageGenerationOutput,
)


MOCK_IMAGE_NOTE = "Mock image generation result. No real GPU or ComfyUI call was made."


def _get_mock_dimensions(aspect_ratio: str) -> tuple[int, int]:
    if aspect_ratio == "16:9":
        return 1920, 1080

    if aspect_ratio == "1:1":
        return 1024, 1024

    return 1080, 1920


def _get_mock_seed(base_seed: int | None, output_index: int, output_count: int) -> int | None:
    if base_seed is None:
        return None

    if output_count == 1:
        return base_seed

    return base_seed + output_index - 1


def generate_image_generation_mock(input_data: ImageGenerationInput) -> ImageGenerationOutput:
    items: list[ImageGenerationItem] = []

    for prompt_item in input_data.prompt_items:
        width, height = _get_mock_dimensions(prompt_item.aspect_ratio)
        base_seed = prompt_item.seed if prompt_item.seed is not None else input_data.seed

        for output_index in range(1, input_data.output_count + 1):
            task_id = f"mock-img-{prompt_item.prompt_id}-{output_index}"

            items.append(
                ImageGenerationItem(
                    task_id=task_id,
                    prompt_id=prompt_item.prompt_id,
                    shot_id=prompt_item.shot_id,
                    status="succeeded",
                    positive_prompt=prompt_item.positive_prompt,
                    negative_prompt=prompt_item.negative_prompt,
                    provider=input_data.provider,
                    workflow_name=input_data.workflow_name,
                    image_url=None,
                    mock_url=f"/mock/images/{task_id}.png",
                    local_path=f"mock_outputs/images/{task_id}.png",
                    width=width,
                    height=height,
                    seed=_get_mock_seed(base_seed, output_index, input_data.output_count),
                    metadata={
                        "source": "mock",
                        "aspect_ratio": prompt_item.aspect_ratio,
                        "style_preset": prompt_item.style_preset,
                        "output_index": output_index,
                        "note": MOCK_IMAGE_NOTE,
                    },
                    error_message=None,
                )
            )

    return ImageGenerationOutput(
        project_title=input_data.project_title,
        provider=input_data.provider,
        status="succeeded",
        items=items,
        metadata={
            "source": "mock",
            "workflow_name": input_data.workflow_name,
            "note": MOCK_IMAGE_NOTE,
        },
    )


def generate_image_generation(input_data: ImageGenerationInput) -> ImageGenerationOutput:
    return generate_image_generation_mock(input_data)
