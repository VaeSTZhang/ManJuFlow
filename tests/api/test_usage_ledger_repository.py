from pathlib import Path
import sqlite3
import sys


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.repositories.usage_ledger_repository import (  # noqa: E402
    SQLiteUsageLedgerRepository,
    UsageLedgerRecord,
)


SAFE_METADATA_JSON = '{"characters_count": 4, "episode_count": 3}'
FORBIDDEN_LEDGER_CONTENT = [
    "source_text",
    "api_key",
    "password",
    "password_hash",
    "access_token",
    "session_token",
    "provider_raw_response",
    "full_response",
    "/Users/",
]


def build_usage_record(**overrides) -> UsageLedgerRecord:
    data = {
        "id": "usage_request_001",
        "request_id": "request_001",
        "user_id": "user_safe_creator_001",
        "username": "safe_creator",
        "workspace_id": "workspace_dramora_internal",
        "project_id": "project_creation_default",
        "session_id": "session_safe_creator_001",
        "context_policy": "current_project_only",
        "operation": "script_generation",
        "purpose": "script_generation",
        "provider": "deepseek",
        "model": "deepseek-chat",
        "generation_mode": "llm",
        "status": "success",
        "source_mode": "idea",
        "document_operation": None,
        "input_character_count": 120,
        "output_character_count": 2400,
        "prompt_token_count": 180,
        "completion_token_count": 640,
        "total_token_count": 820,
        "estimated_cost_cny": 0.08,
        "latency_ms": 1200,
        "error_code": None,
        "error_message_safe": None,
        "created_at": "2026-05-06T10:00:00+00:00",
        "metadata_json": SAFE_METADATA_JSON,
    }
    data.update(overrides)
    return UsageLedgerRecord(**data)


def assert_record_has_no_forbidden_content(record: UsageLedgerRecord) -> None:
    dumped = str(record)
    for forbidden in FORBIDDEN_LEDGER_CONTENT:
        assert forbidden not in dumped


def assert_metadata_json_is_safe(metadata_json: str | None) -> None:
    assert metadata_json is not None
    for forbidden in FORBIDDEN_LEDGER_CONTENT:
        assert forbidden not in metadata_json


def make_repository(tmp_path: Path) -> SQLiteUsageLedgerRepository:
    repository = SQLiteUsageLedgerRepository(tmp_path / "usage_ledger_test.sqlite")
    repository.init_schema()
    return repository


def test_init_schema_creates_usage_ledger_table(tmp_path: Path) -> None:
    repository = SQLiteUsageLedgerRepository(tmp_path / "usage_ledger_test.sqlite")

    repository.init_schema()
    repository.init_schema()

    with sqlite3.connect(tmp_path / "usage_ledger_test.sqlite") as connection:
        table = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'usage_ledger'"
        ).fetchone()

    assert table is not None


def test_create_entry_and_get_entry_by_request_id(tmp_path: Path) -> None:
    repository = make_repository(tmp_path)
    record = build_usage_record()

    repository.create_entry(record)
    fetched = repository.get_entry_by_request_id("request_001")

    assert fetched == record
    assert fetched is not None
    assert fetched.context_policy == "current_project_only"
    assert_metadata_json_is_safe(fetched.metadata_json)
    assert_record_has_no_forbidden_content(fetched)


def test_get_entry_by_request_id_returns_none_for_missing_request(tmp_path: Path) -> None:
    repository = make_repository(tmp_path)

    assert repository.get_entry_by_request_id("missing_request") is None
    assert repository.get_entry_by_request_id(" ") is None


def test_list_entries_orders_by_created_at_desc(tmp_path: Path) -> None:
    repository = make_repository(tmp_path)
    repository.create_entry(
        build_usage_record(id="usage_old", request_id="request_old", created_at="2026-05-06T09:00:00+00:00")
    )
    repository.create_entry(
        build_usage_record(id="usage_new", request_id="request_new", created_at="2026-05-06T11:00:00+00:00")
    )

    entries = repository.list_entries()

    assert [entry.id for entry in entries] == ["usage_new", "usage_old"]


def test_list_entries_limit_is_applied(tmp_path: Path) -> None:
    repository = make_repository(tmp_path)
    repository.create_entry(build_usage_record(id="usage_001", request_id="request_001"))
    repository.create_entry(build_usage_record(id="usage_002", request_id="request_002"))

    entries = repository.list_entries(limit=1)

    assert len(entries) == 1


def test_list_entries_filters_by_user_id(tmp_path: Path) -> None:
    repository = make_repository(tmp_path)
    repository.create_entry(build_usage_record(id="usage_safe", request_id="request_safe"))
    repository.create_entry(
        build_usage_record(
            id="usage_other",
            request_id="request_other",
            user_id="user_safe_reviewer_001",
        )
    )

    entries = repository.list_entries(user_id="user_safe_creator_001")

    assert [entry.id for entry in entries] == ["usage_safe"]


def test_list_entries_filters_by_workspace_id(tmp_path: Path) -> None:
    repository = make_repository(tmp_path)
    repository.create_entry(build_usage_record(id="usage_internal", request_id="request_internal"))
    repository.create_entry(
        build_usage_record(
            id="usage_other_workspace",
            request_id="request_other_workspace",
            workspace_id="workspace_safe_other",
        )
    )

    entries = repository.list_entries(workspace_id="workspace_dramora_internal")

    assert [entry.id for entry in entries] == ["usage_internal"]


def test_list_entries_filters_by_project_id(tmp_path: Path) -> None:
    repository = make_repository(tmp_path)
    repository.create_entry(build_usage_record(id="usage_creation", request_id="request_creation"))
    repository.create_entry(
        build_usage_record(
            id="usage_other_project",
            request_id="request_other_project",
            project_id="project_safe_other",
        )
    )

    entries = repository.list_entries(project_id="project_creation_default")

    assert [entry.id for entry in entries] == ["usage_creation"]


def test_create_failed_entry_with_safe_error_fields(tmp_path: Path) -> None:
    repository = make_repository(tmp_path)
    record = build_usage_record(
        id="usage_failed",
        request_id="request_failed",
        status="failed",
        estimated_cost_cny=None,
        error_code="script_generation_contract_failed",
        error_message_safe="target_episode_count contract failed",
        metadata_json='{"requested_episode_count": 3, "actual_episode_count": 1}',
    )

    repository.create_entry(record)
    fetched = repository.get_entry_by_request_id("request_failed")

    assert fetched is not None
    assert fetched.status == "failed"
    assert fetched.error_code == "script_generation_contract_failed"
    assert fetched.error_message_safe == "target_episode_count contract failed"
    assert_metadata_json_is_safe(fetched.metadata_json)
    assert_record_has_no_forbidden_content(fetched)


def test_summarize_by_user_counts_statuses_and_cost(tmp_path: Path) -> None:
    repository = make_repository(tmp_path)
    repository.create_entry(build_usage_record(id="usage_success", request_id="request_success", estimated_cost_cny=0.08))
    repository.create_entry(
        build_usage_record(
            id="usage_failed",
            request_id="request_failed",
            status="failed",
            estimated_cost_cny=0.02,
        )
    )

    summaries = repository.summarize_by_user()
    summary = next(item for item in summaries if item["user_id"] == "user_safe_creator_001")

    assert summary["entry_count"] == 2
    assert summary["success_count"] == 1
    assert summary["failed_count"] == 1
    assert summary["estimated_cost_cny_total"] == 0.1


def test_summarize_by_provider_groups_cost(tmp_path: Path) -> None:
    repository = make_repository(tmp_path)
    repository.create_entry(build_usage_record(id="usage_deepseek", request_id="request_deepseek", estimated_cost_cny=0.08))
    repository.create_entry(
        build_usage_record(
            id="usage_kimi",
            request_id="request_kimi",
            provider="kimi",
            model="kimi-k2.5",
            estimated_cost_cny=0.04,
        )
    )

    summaries = repository.summarize_by_provider()

    assert any(
        item["provider"] == "deepseek"
        and item["entry_count"] == 1
        and item["estimated_cost_cny_total"] == 0.08
        for item in summaries
    )
    assert any(
        item["provider"] == "kimi"
        and item["entry_count"] == 1
        and item["estimated_cost_cny_total"] == 0.04
        for item in summaries
    )


def test_summarize_by_operation_counts_statuses(tmp_path: Path) -> None:
    repository = make_repository(tmp_path)
    repository.create_entry(build_usage_record(id="usage_script_success", request_id="request_script_success"))
    repository.create_entry(
        build_usage_record(
            id="usage_script_failed",
            request_id="request_script_failed",
            status="failed",
        )
    )
    repository.create_entry(
        build_usage_record(
            id="usage_export",
            request_id="request_export",
            operation="document_export",
            document_operation="export_docx",
        )
    )

    summaries = repository.summarize_by_operation()
    script_summary = next(item for item in summaries if item["operation"] == "script_generation")
    export_summary = next(item for item in summaries if item["operation"] == "document_export")

    assert script_summary["entry_count"] == 2
    assert script_summary["success_count"] == 1
    assert script_summary["failed_count"] == 1
    assert export_summary["entry_count"] == 1
    assert export_summary["success_count"] == 1
    assert export_summary["failed_count"] == 0


def test_metadata_json_sample_does_not_contain_sensitive_fields() -> None:
    assert_metadata_json_is_safe(SAFE_METADATA_JSON)


def test_repository_tests_use_tmp_path(tmp_path: Path) -> None:
    repository = make_repository(tmp_path)
    repository.create_entry(build_usage_record())

    assert (tmp_path / "usage_ledger_test.sqlite").exists()
    assert not Path("usage_ledger_test.sqlite").exists()
