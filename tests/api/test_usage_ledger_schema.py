from pathlib import Path
import sys

import pytest
from pydantic import ValidationError


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.schemas.context import ContextOptions
from app.schemas.usage_ledger import (  # noqa: E402
    UsageLedgerCostEstimate,
    UsageLedgerEntry,
    UsageLedgerSummary,
)


def test_usage_ledger_cost_estimate_can_be_created() -> None:
    cost = UsageLedgerCostEstimate(
        input_tokens=120,
        output_tokens=240,
        total_tokens=360,
        estimated_cost_cny=0.08,
    )

    assert cost.currency == "CNY"
    assert cost.total_tokens == 360
    assert cost.estimated_cost_cny == 0.08


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("input_tokens", -1),
        ("output_tokens", -1),
        ("total_tokens", -1),
        ("estimated_cost_cny", -0.01),
    ],
)
def test_usage_ledger_cost_estimate_rejects_negative_values(field: str, value: int | float) -> None:
    with pytest.raises(ValidationError):
        UsageLedgerCostEstimate(**{field: value})


def test_usage_ledger_entry_can_include_context_options() -> None:
    entry = UsageLedgerEntry(
        ledger_id="usage_request_001",
        operation="script_generation",
        status="success",
        context=ContextOptions(
            user_id="internal_user_001",
            workspace_id="workspace_dramora_internal",
            project_id="project_lights_return",
            session_id="session_script_generation",
        ),
        provider="deepseek",
        model="deepseek-chat",
        purpose="script_generation",
        source_mode="idea",
        source_stage="generated_script",
        request_id="request_001",
    )

    assert entry.context is not None
    assert entry.context.project_id == "project_lights_return"
    assert entry.context.context_policy == "current_project_only"
    assert entry.provider == "deepseek"
    assert entry.model == "deepseek-chat"


def test_usage_ledger_entry_metadata_defaults_are_independent() -> None:
    first_entry = UsageLedgerEntry(
        ledger_id="usage_001",
        operation="document_export",
        status="success",
    )
    second_entry = UsageLedgerEntry(
        ledger_id="usage_002",
        operation="document_import",
        status="success",
    )

    first_entry.metadata["source_stage"] = "export"

    assert second_entry.metadata == {}


def test_usage_ledger_entry_does_not_require_full_script_content() -> None:
    entry = UsageLedgerEntry(
        ledger_id="usage_request_002",
        operation="film_adaptation",
        status="failed",
        error_code="script_generation_contract_failed",
        error_message="Generated script does not match requested target_episode_count.",
        metadata={"source_mode": "film_script"},
    )
    dumped = entry.model_dump()

    assert "source_text" not in dumped
    assert "full_response" not in dumped
    assert "api_key" not in dumped


def test_usage_ledger_entry_rejects_empty_ledger_id() -> None:
    with pytest.raises(ValidationError):
        UsageLedgerEntry(
            ledger_id="",
            operation="script_generation",
            status="success",
        )


def test_usage_ledger_entry_rejects_negative_duration() -> None:
    with pytest.raises(ValidationError):
        UsageLedgerEntry(
            ledger_id="usage_request_003",
            operation="script_generation",
            status="success",
            duration_ms=-1,
        )


def test_usage_ledger_summary_can_be_created() -> None:
    summary = UsageLedgerSummary(
        total_entries=3,
        success_count=1,
        failed_count=1,
        blocked_count=1,
        estimated_total_cost_cny=0.12,
    )

    assert summary.total_entries == 3
    assert summary.currency == "CNY"
    assert summary.estimated_total_cost_cny == 0.12
