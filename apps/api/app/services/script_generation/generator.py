from app.config import get_settings
from app.schemas.idea import IdeaInput
from app.schemas.script import ScriptOutput
from app.schemas.script_generation import ShortDramaGenerationInput, ShortDramaScriptOutput
from app.services.script_generation.film_adaptation import generate_film_script_adaptation_mock
from app.services.script_generation.metadata import build_script_generation_metadata
from app.services.script_generation.novel_adaptation import generate_novel_adaptation_mock
from app.services.script_service import generate_script_mock


def _build_idea_input(input_data: ShortDramaGenerationInput) -> IdeaInput:
    idea_text = (input_data.idea_text or "").strip()
    if not idea_text:
        raise ValueError("source_mode='idea' requires idea_text.")

    return IdeaInput(
        idea_text=idea_text,
        script_type="短剧",
        genre=input_data.genre,
        episode_count=input_data.target_episode_count,
        episode_duration=input_data.duration_per_episode or "3-5分钟",
        target_platform=input_data.target_audience or "短视频平台",
        tone=input_data.style,
        audience=input_data.target_audience or "短剧观众",
        style_requirements=input_data.extra_requirements,
    )


def _map_script_output_to_short_drama_output(
    script_output: ScriptOutput,
    input_data: ShortDramaGenerationInput,
) -> ShortDramaScriptOutput:
    metadata = build_script_generation_metadata(input_data)
    metadata["bridge_from"] = "ScriptOutput"

    return ShortDramaScriptOutput(
        project_title=script_output.project_title,
        source_mode="idea",
        logline=script_output.logline,
        world_setting=script_output.world_setting,
        characters=script_output.characters,
        adaptation_notes=None,
        episode_count=len(script_output.episodes),
        episodes=script_output.episodes,
        metadata=metadata,
    )


def generate_short_drama_script_mock(
    input_data: ShortDramaGenerationInput,
) -> ShortDramaScriptOutput:
    if input_data.source_mode == "idea":
        script_output = generate_script_mock(_build_idea_input(input_data))
        return _map_script_output_to_short_drama_output(script_output, input_data)

    if input_data.source_mode == "film_script":
        return generate_film_script_adaptation_mock(input_data)

    if input_data.source_mode == "novel":
        return generate_novel_adaptation_mock(input_data)

    if input_data.source_mode == "assistant_rewrite":
        raise NotImplementedError(
            "source_mode='assistant_rewrite' is not implemented in the three-entry mock "
            "service yet; it will be handled by the Assistant module."
        )

    if input_data.source_mode == "uploaded_document":
        raise NotImplementedError(
            "source_mode='uploaded_document' is not implemented in the three-entry mock "
            "service yet; it will be handled by Document Import."
        )

    raise ValueError(f"Unsupported source_mode: {input_data.source_mode}")


def generate_short_drama_script(
    input_data: ShortDramaGenerationInput,
) -> ShortDramaScriptOutput:
    mode = get_settings().script_generation_mode.lower()

    if mode == "mock":
        return generate_short_drama_script_mock(input_data)

    if mode == "llm":
        raise NotImplementedError(
            "SCRIPT_GENERATION_MODE=llm is not implemented for generate-from-source yet."
        )

    raise ValueError("SCRIPT_GENERATION_MODE only supports 'mock' or 'llm'.")
