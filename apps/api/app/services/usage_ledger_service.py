from datetime import UTC, datetime
import json
import os
from pathlib import Path
import re

from app.repositories.usage_ledger_repository import SQLiteUsageLedgerRepository, UsageLedgerRecord
from app.schemas.usage_ledger import (
    UsageLedgerCreate,
    UsageLedgerEntry,
    UsageLedgerMetadataValue,
    UsageLedgerSummary,
)


DANGEROUS_USAGE_METADATA_KEYS = {
    "api_key",
    "access_token",
    "extracted_text",
    "full_response",
    "password",
    "password_hash",
    "provider_raw_response",
    "source_text",
    "token",
}
DEFAULT_USAGE_LEDGER_ID = "usage_mock_001"
USAGE_LEDGER_DB_PATH_ENV_VAR = "DRAMORA_USAGE_LEDGER_DB_PATH"
DEFAULT_USAGE_LEDGER_DB_PATH = Path(".local") / "dramora_usage_ledger.sqlite3"

_usage_ledger_repository_override: SQLiteUsageLedgerRepository | None = None
_default_usage_ledger_repository: SQLiteUsageLedgerRepository | None = None


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


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


def get_default_usage_ledger_database_path() -> Path:
    configured_path = os.getenv(USAGE_LEDGER_DB_PATH_ENV_VAR)
    if configured_path:
        return Path(configured_path)
    return DEFAULT_USAGE_LEDGER_DB_PATH


def get_usage_ledger_repository() -> SQLiteUsageLedgerRepository:
    if _usage_ledger_repository_override is not None:
        return _usage_ledger_repository_override

    global _default_usage_ledger_repository
    if _default_usage_ledger_repository is None:
        database_path = get_default_usage_ledger_database_path()
        database_path.parent.mkdir(parents=True, exist_ok=True)
        _default_usage_ledger_repository = SQLiteUsageLedgerRepository(database_path)
        _default_usage_ledger_repository.init_schema()

    return _default_usage_ledger_repository


def configure_usage_ledger_repository_for_testing(
    repository: SQLiteUsageLedgerRepository,
) -> None:
    global _usage_ledger_repository_override
    repository.init_schema()
    _usage_ledger_repository_override = repository


def reset_usage_ledger_repository_for_testing() -> None:
    global _usage_ledger_repository_override
    _usage_ledger_repository_override = None


def create_usage_ledger_entry(input_data: UsageLedgerCreate) -> UsageLedgerEntry:
    usage_entry = UsageLedgerEntry(
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
    get_usage_ledger_repository().create_entry(_build_usage_ledger_record(usage_entry))
    return usage_entry


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


def _build_usage_ledger_record(entry: UsageLedgerEntry) -> UsageLedgerRecord:
    context = entry.context
    cost_estimate = entry.cost_estimate
    metadata_json = json.dumps(entry.metadata, ensure_ascii=False, sort_keys=True)

    return UsageLedgerRecord(
        id=entry.ledger_id,
        request_id=entry.request_id or (context.request_id if context else None),
        user_id=context.user_id if context else None,
        username=None,
        workspace_id=context.workspace_id if context else None,
        project_id=context.project_id if context else None,
        session_id=context.session_id if context else None,
        context_policy=context.context_policy if context else "current_project_only",
        operation=entry.operation,
        purpose=entry.purpose,
        provider=entry.provider,
        model=entry.model,
        generation_mode=str(entry.metadata.get("generation_mode")) if entry.metadata.get("generation_mode") else None,
        status=entry.status,
        source_mode=entry.source_mode,
        document_operation=None,
        input_character_count=_metadata_int(entry.metadata.get("input_character_count")),
        output_character_count=_metadata_int(entry.metadata.get("output_character_count")),
        prompt_token_count=cost_estimate.input_tokens if cost_estimate else None,
        completion_token_count=cost_estimate.output_tokens if cost_estimate else None,
        total_token_count=cost_estimate.total_tokens if cost_estimate else None,
        estimated_cost_cny=cost_estimate.estimated_cost_cny if cost_estimate else None,
        latency_ms=entry.duration_ms,
        error_code=entry.error_code,
        error_message_safe=entry.error_message,
        created_at=entry.finished_at or entry.started_at or _utc_now_iso(),
        metadata_json=metadata_json,
    )


def _metadata_int(value: UsageLedgerMetadataValue) -> int | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    return None
