from pathlib import Path
import sys


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.schemas.context import ContextOptions
from app.schemas.usage_ledger import UsageLedgerCostEstimate, UsageLedgerCreate
from app.services.usage_ledger_service import (
    create_usage_ledger_entry,
    summarize_usage_ledger,
)


def test_create_usage_ledger_entry_returns_ledger_id() -> None:
    entry = create_usage_ledger_entry(
        UsageLedgerCreate(
            operation="script_generation",
            status="success",
            request_id="request_001",
        )
    )

    assert entry.ledger_id == "usage_request_001"
    assert entry.request_id == "request_001"


def test_create_usage_ledger_entry_preserves_context_project_and_session() -> None:
    entry = create_usage_ledger_entry(
        UsageLedgerCreate(
            operation="film_adaptation",
            status="success",
            context=ContextOptions(
                project_id="project_old_cinema",
                session_id="session_film_adaptation",
                request_id="context_request_001",
            ),
        )
    )

    assert entry.context is not None
    assert entry.context.project_id == "project_old_cinema"
    assert entry.context.session_id == "session_film_adaptation"
    assert entry.ledger_id == "usage_context_request_001"


def test_create_usage_ledger_entry_preserves_model_tracking_fields() -> None:
    entry = create_usage_ledger_entry(
        UsageLedgerCreate(
            operation="novel_adaptation",
            status="success",
            provider="deepseek",
            model="deepseek-chat",
            purpose="novel_adaptation",
            source_mode="novel",
            source_stage="generated_script",
            prompt_template_name="novel_to_short_drama_v1.md",
        )
    )

    assert entry.provider == "deepseek"
    assert entry.model == "deepseek-chat"
    assert entry.purpose == "novel_adaptation"
    assert entry.source_mode == "novel"
    assert entry.prompt_template_name == "novel_to_short_drama_v1.md"


def test_create_usage_ledger_entry_filters_sensitive_metadata() -> None:
    entry = create_usage_ledger_entry(
        UsageLedgerCreate(
            operation="script_generation",
            status="failed",
            metadata={
                "source_text": "不应记录的完整原文",
                "extracted_text": "不应记录的上传内容",
                "full_response": "不应记录的 provider 原始响应",
                "api_key": "not-a-real-key",
                "safe_flag": True,
            },
        )
    )

    assert entry.metadata == {"safe_flag": True}


def test_summarize_usage_ledger_counts_statuses() -> None:
    entries = [
        create_usage_ledger_entry(
            UsageLedgerCreate(operation="script_generation", status="success", request_id="request_success")
        ),
        create_usage_ledger_entry(
            UsageLedgerCreate(operation="document_export", status="failed", request_id="request_failed")
        ),
        create_usage_ledger_entry(
            UsageLedgerCreate(operation="quality_review", status="blocked", request_id="request_blocked")
        ),
        create_usage_ledger_entry(
            UsageLedgerCreate(operation="document_import", status="skipped", request_id="request_skipped")
        ),
    ]

    summary = summarize_usage_ledger(entries)

    assert summary.total_entries == 4
    assert summary.success_count == 1
    assert summary.failed_count == 1
    assert summary.blocked_count == 1


def test_summarize_usage_ledger_accumulates_estimated_cost_cny() -> None:
    entries = [
        create_usage_ledger_entry(
            UsageLedgerCreate(
                operation="script_generation",
                status="success",
                request_id="request_cost_001",
                cost_estimate=UsageLedgerCostEstimate(estimated_cost_cny=0.05),
            )
        ),
        create_usage_ledger_entry(
            UsageLedgerCreate(
                operation="film_adaptation",
                status="success",
                request_id="request_cost_002",
                cost_estimate=UsageLedgerCostEstimate(estimated_cost_cny=0.07),
            )
        ),
        create_usage_ledger_entry(
            UsageLedgerCreate(
                operation="document_export",
                status="success",
                request_id="request_cost_003",
            )
        ),
    ]

    summary = summarize_usage_ledger(entries)

    assert summary.estimated_total_cost_cny == 0.12
    assert summary.currency == "CNY"
