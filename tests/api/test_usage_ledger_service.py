from pathlib import Path
import sys

import pytest


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.repositories.usage_ledger_repository import SQLiteUsageLedgerRepository
from app.schemas.context import ContextOptions
from app.schemas.usage_ledger import UsageLedgerCostEstimate, UsageLedgerCreate
from app.services.usage_ledger_service import (
    configure_usage_ledger_repository_for_testing,
    create_usage_ledger_entry,
    reset_usage_ledger_repository_for_testing,
    summarize_usage_ledger,
)


@pytest.fixture(autouse=True)
def isolated_usage_ledger_repository(tmp_path: Path):
    repository = SQLiteUsageLedgerRepository(tmp_path / "usage_ledger_service_test.sqlite")
    configure_usage_ledger_repository_for_testing(repository)
    yield repository
    reset_usage_ledger_repository_for_testing()


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


def test_create_usage_ledger_entry_persists_success_entry(
    isolated_usage_ledger_repository: SQLiteUsageLedgerRepository,
) -> None:
    entry = create_usage_ledger_entry(
        UsageLedgerCreate(
            operation="script_generation",
            status="success",
            context=ContextOptions(
                user_id="user_safe_creator_001",
                workspace_id="workspace_dramora_internal",
                project_id="project_creation_default",
                session_id="session_safe_creator_001",
                request_id="request_persist_success",
            ),
            provider="deepseek",
            model="deepseek-chat",
            purpose="script_generation",
            source_mode="idea",
            metadata={
                "generation_mode": "mock",
                "input_character_count": 12,
                "output_character_count": 120,
            },
        )
    )

    stored = isolated_usage_ledger_repository.get_entry_by_request_id("request_persist_success")

    assert stored is not None
    assert stored.id == entry.ledger_id
    assert stored.user_id == "user_safe_creator_001"
    assert stored.workspace_id == "workspace_dramora_internal"
    assert stored.project_id == "project_creation_default"
    assert stored.session_id == "session_safe_creator_001"
    assert stored.context_policy == "current_project_only"
    assert stored.operation == "script_generation"
    assert stored.status == "success"
    assert stored.provider == "deepseek"
    assert stored.model == "deepseek-chat"
    assert stored.purpose == "script_generation"
    assert stored.source_mode == "idea"
    assert stored.generation_mode == "mock"
    assert stored.input_character_count == 12
    assert stored.output_character_count == 120


def test_create_usage_ledger_entry_persists_failed_entry(
    isolated_usage_ledger_repository: SQLiteUsageLedgerRepository,
) -> None:
    create_usage_ledger_entry(
        UsageLedgerCreate(
            operation="film_adaptation",
            status="failed",
            context=ContextOptions(request_id="request_persist_failed"),
            source_mode="film_script",
            error_code="script_generation_contract_failed",
            error_message="target_episode_count contract failed",
            metadata={
                "source_text": "不应记录的完整原文",
                "provider_raw_response": "不应记录的 provider 原始响应",
                "api_key": "not-a-real-key",
                "safe_flag": True,
            },
        )
    )

    stored = isolated_usage_ledger_repository.get_entry_by_request_id("request_persist_failed")

    assert stored is not None
    assert stored.status == "failed"
    assert stored.error_code == "script_generation_contract_failed"
    assert stored.error_message_safe == "target_episode_count contract failed"
    assert stored.metadata_json == '{"safe_flag": true}'
    stored_text = str(stored)
    assert "source_text" not in stored_text
    assert "provider_raw_response" not in stored_text
    assert "api_key" not in stored_text
    assert "not-a-real-key" not in stored_text


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
