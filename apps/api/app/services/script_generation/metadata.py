from typing import Any

from app.schemas.script_generation import ShortDramaGenerationInput


def build_script_generation_metadata(
    input_data: ShortDramaGenerationInput,
    generation_mode: str = "mock",
) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "generation_mode": generation_mode,
        "source_mode": input_data.source_mode,
        "context_policy": (
            input_data.context_options.context_policy
            if input_data.context_options is not None
            else "current_project_only"
        ),
    }

    if input_data.context_options is not None:
        metadata["context"] = input_data.context_options.model_dump(exclude_none=True)

    if input_data.ai_options is None:
        return metadata

    ai_options = input_data.ai_options.model_dump()
    metadata["ai_options"] = ai_options

    if input_data.ai_options.provider:
        metadata["provider"] = input_data.ai_options.provider

    if input_data.ai_options.model:
        metadata["model"] = input_data.ai_options.model

    if input_data.ai_options.purpose:
        metadata["purpose"] = input_data.ai_options.purpose

    return metadata
