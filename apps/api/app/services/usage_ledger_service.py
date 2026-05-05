import re

from app.schemas.usage_ledger import (
    UsageLedgerCreate,
    UsageLedgerEntry,
    UsageLedgerMetadataValue,
    UsageLedgerSummary,
)


DANGEROUS_USAGE_METADATA_KEYS = {
    "api_key",
    "extracted_text",
    "full_response",
    "provider_raw_response",
    "source_text",
}
DEFAULT_USAGE_LEDGER_ID = "usage_mock_001"


def _safe_id_part(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    return cleaned.strip("_.-") or "request"


def _build_usage_ledger_id(input_data: UsageLedgerCreate) -> str:
    if input_data.request_id:
        return f"usage_{_safe_id_part(input_data.request_id)}"
    if input_data.context and input_data.context.request_id:
        return f"usage_{_safe_id_part(input_data.context.request_id)}"
    return DEFAULT_USAGE_LEDGER_ID


def _sanitize_usage_metadata(
    metadata: dict[str, UsageLedgerMetadataValue],
) -> dict[str, UsageLedgerMetadataValue]:
    return {
        key: value
        for key, value in metadata.items()
        if key not in DANGEROUS_USAGE_METADATA_KEYS
    }


def create_usage_ledger_entry(input_data: UsageLedgerCreate) -> UsageLedgerEntry:
    return UsageLedgerEntry(
        ledger_id=_build_usage_ledger_id(input_data),
        operation=input_data.operation,
        status=input_data.status,
        context=input_data.context,
        provider=input_data.provider,
        model=input_data.model,
        purpose=input_data.purpose,
        source_mode=input_data.source_mode,
        source_stage=input_data.source_stage,
        prompt_template_name=input_data.prompt_template_name,
        request_id=input_data.request_id,
        duration_ms=input_data.duration_ms,
        cost_estimate=input_data.cost_estimate,
        error_code=input_data.error_code,
        error_message=input_data.error_message,
        metadata=_sanitize_usage_metadata(input_data.metadata),
    )


def summarize_usage_ledger(entries: list[UsageLedgerEntry]) -> UsageLedgerSummary:
    estimated_total_cost_cny = round(
        sum(
            entry.cost_estimate.estimated_cost_cny or 0
            for entry in entries
            if entry.cost_estimate is not None
        ),
        6,
    )

    return UsageLedgerSummary(
        total_entries=len(entries),
        success_count=sum(1 for entry in entries if entry.status == "success"),
        failed_count=sum(1 for entry in entries if entry.status == "failed"),
        blocked_count=sum(1 for entry in entries if entry.status == "blocked"),
        estimated_total_cost_cny=estimated_total_cost_cny,
    )
