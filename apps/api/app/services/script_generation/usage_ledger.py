from app.schemas.script_generation import ShortDramaGenerationInput, ShortDramaScriptOutput
from app.schemas.usage_ledger import UsageLedgerCreate, UsageLedgerOperation, UsageLedgerStatus
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
                "generation_mode": metadata.get("generation_mode"),
                "source_mode": input_data.source_mode,
            },
        )
    )
    metadata["usage_ledger"] = usage_entry.model_dump(exclude_none=True)

    return output.model_copy(update={"metadata": metadata})
