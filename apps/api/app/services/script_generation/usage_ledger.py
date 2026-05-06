from app.schemas.script_generation import ShortDramaGenerationInput, ShortDramaScriptOutput
from app.schemas.usage_ledger import UsageLedgerCreate, UsageLedgerOperation, UsageLedgerStatus
from app.services.script_generation.validation import resolve_target_episode_count
from app.services.usage_ledger_service import create_usage_ledger_entry


SCRIPT_GENERATION_OPERATION_BY_SOURCE_MODE: dict[str, UsageLedgerOperation] = {
    "idea": "script_generation",
    "film_script": "film_adaptation",
    "novel": "novel_adaptation",
}


def _resolve_usage_operation(source_mode: str) -> UsageLedgerOperation:
    return SCRIPT_GENERATION_OPERATION_BY_SOURCE_MODE.get(source_mode, "script_generation")


def attach_usage_ledger_metadata(
    output: ShortDramaScriptOutput,
    input_data: ShortDramaGenerationInput,
    status: UsageLedgerStatus = "success",
) -> ShortDramaScriptOutput:
    metadata = dict(output.metadata)
    ai_options = input_data.ai_options
    context = input_data.context_options

    usage_entry = create_usage_ledger_entry(
        UsageLedgerCreate(
            operation=_resolve_usage_operation(input_data.source_mode),
            status=status,
            context=context,
            provider=(
                ai_options.provider
                if ai_options and ai_options.provider
                else metadata.get("provider")
            ),
            model=(
                ai_options.model
                if ai_options and ai_options.model
                else metadata.get("model")
            ),
            purpose=(
                ai_options.purpose
                if ai_options and ai_options.purpose
                else metadata.get("purpose")
            ),
            source_mode=input_data.source_mode,
            source_stage=(
                context.source_stage
                if context and context.source_stage
                else "generated_script"
            ),
            prompt_template_name=metadata.get("prompt_template_name"),
            request_id=(
                context.request_id
                if context and context.request_id
                else None
            ),
            metadata={
                "characters_count": len(output.characters),
                "episode_count": output.episode_count,
                "generation_mode": metadata.get("generation_mode"),
                "input_character_count": _input_character_count(input_data),
                "output_character_count": _output_character_count(output),
                "source_mode": input_data.source_mode,
                "target_episode_count": _safe_resolved_target_episode_count(input_data),
            },
        )
    )
    metadata["usage_ledger"] = usage_entry.model_dump(exclude_none=True)

    return output.model_copy(update={"metadata": metadata})


def record_script_generation_failure_usage(
    input_data: ShortDramaGenerationInput,
    error_code: str,
    error_message_safe: str,
) -> None:
    ai_options = input_data.ai_options
    context = input_data.context_options
    create_usage_ledger_entry(
        UsageLedgerCreate(
            operation=_resolve_usage_operation(input_data.source_mode),
            status="failed",
            context=context,
            provider=ai_options.provider if ai_options and ai_options.provider else None,
            model=ai_options.model if ai_options and ai_options.model else None,
            purpose=ai_options.purpose if ai_options and ai_options.purpose else None,
            source_mode=input_data.source_mode,
            source_stage=(
                context.source_stage
                if context and context.source_stage
                else "generated_script"
            ),
            request_id=(
                context.request_id
                if context and context.request_id
                else None
            ),
            error_code=error_code,
            error_message=error_message_safe,
            metadata={
                "input_character_count": _input_character_count(input_data),
                "source_mode": input_data.source_mode,
                "target_episode_count": _safe_resolved_target_episode_count(input_data),
            },
        )
    )


def _input_character_count(input_data: ShortDramaGenerationInput) -> int:
    return len(input_data.idea_text or "") + len(input_data.source_text or "")


def _safe_resolved_target_episode_count(input_data: ShortDramaGenerationInput) -> int | None:
    try:
        return resolve_target_episode_count(input_data)
    except ValueError:
        return None


def _output_character_count(output: ShortDramaScriptOutput) -> int:
    text_parts: list[str] = [
        output.project_title,
        output.logline,
        output.world_setting,
    ]
    for character in output.characters:
        text_parts.extend([
            character.name,
            character.role,
            character.age,
            character.personality,
            character.arc,
        ])
    for episode in output.episodes:
        text_parts.extend([episode.title, episode.summary, episode.hook])
        for scene in episode.scenes:
            text_parts.extend([
                scene.location,
                scene.time,
                scene.description,
                scene.visual_notes,
                scene.emotion_curve,
            ])
            for dialogue in scene.dialogues:
                text_parts.extend([dialogue.character, dialogue.line])
    return sum(len(part or "") for part in text_parts)
