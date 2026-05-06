from pathlib import Path
import sys

import pytest


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.repositories.ownership_repository import SQLiteOwnershipRepository  # noqa: E402
from app.repositories.usage_ledger_repository import SQLiteUsageLedgerRepository  # noqa: E402
from app.schemas.context import ContextOptions  # noqa: E402
from app.schemas.document import DocumentExportInput  # noqa: E402
from app.services.document_docx_export_service import build_docx_export_bytes  # noqa: E402
from app.services.document_export_service import export_document  # noqa: E402
from app.services.document_import_service import (  # noqa: E402
    build_document_import_preview,
    build_docx_import_preview,
)
from app.services.usage_ledger_service import (  # noqa: E402
    configure_usage_ledger_repository_for_testing,
    reset_usage_ledger_repository_for_testing,
)
from app.services.ownership_service import (  # noqa: E402
    configure_ownership_repository_for_testing,
    reset_ownership_repository_for_testing,
)


SAFE_IMPORT_TEXT = "旧影院来信\n放映员收到一封写给未来的信。"
SAFE_EXPORT_TEXT = "第一集：林灯回到旧楼，发现父亲留下的剧本。"


@pytest.fixture(autouse=True)
def isolated_usage_ledger_repository(tmp_path: Path):
    usage_repository = SQLiteUsageLedgerRepository(tmp_path / "document_usage_ledger_test.sqlite")
    ownership_repository = SQLiteOwnershipRepository(tmp_path / "document_ownership_test.sqlite")
    configure_usage_ledger_repository_for_testing(usage_repository)
    configure_ownership_repository_for_testing(ownership_repository)
    yield usage_repository
    reset_usage_ledger_repository_for_testing()
    reset_ownership_repository_for_testing()


def assert_metadata_has_no_document_body(metadata_json: str | None) -> None:
    assert metadata_json is not None
    assert "extracted_text" not in metadata_json
    assert "preview_text" not in metadata_json
    assert SAFE_IMPORT_TEXT not in metadata_json
    assert SAFE_EXPORT_TEXT not in metadata_json
    assert "docx bytes" not in metadata_json
    assert "api_key" not in metadata_json
    assert "password" not in metadata_json
    assert "password_hash" not in metadata_json
    assert "access_token" not in metadata_json
    assert "session_token" not in metadata_json
    assert "/Users/" not in metadata_json


def test_document_import_preview_success_writes_usage_ledger(
    isolated_usage_ledger_repository: SQLiteUsageLedgerRepository,
) -> None:
    context_options = ContextOptions(
        user_id="user_safe_creator_001",
        workspace_id="workspace_dramora_internal",
        project_id="project_import_test",
        session_id="session_import_test",
        request_id="request_import_preview",
        source_stage="imported_document",
    )

    output = build_document_import_preview(
        filename="old-cinema-letter.docx",
        extracted_text=SAFE_IMPORT_TEXT,
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        file_size_bytes=4096,
        project_title="测试短剧：旧影院来信",
        context_options=context_options,
    )
    stored = isolated_usage_ledger_repository.get_entry_by_request_id("request_import_preview")

    assert output.status == "preview_ready"
    assert stored is not None
    assert stored.operation == "document_import"
    assert stored.document_operation == "import_preview"
    assert stored.status == "success"
    assert stored.user_id == "user_safe_creator_001"
    assert stored.workspace_id == "workspace_dramora_internal"
    assert stored.project_id == "project_import_test"
    assert stored.session_id == "session_import_test"
    assert stored.context_policy == "current_project_only"
    assert stored.input_character_count is None
    assert stored.metadata_json is not None
    assert '"character_count":' in stored.metadata_json
    assert '"paragraph_count": 2' in stored.metadata_json
    assert '"has_detected_title": true' in stored.metadata_json
    assert_metadata_has_no_document_body(stored.metadata_json)


def test_document_import_parse_failure_writes_safe_failed_usage_ledger(
    isolated_usage_ledger_repository: SQLiteUsageLedgerRepository,
) -> None:
    context_options = ContextOptions(
        project_id="project_import_failed",
        session_id="session_import_failed",
        request_id="request_import_failed",
        source_stage="imported_document",
    )

    with pytest.raises(ValueError):
        build_docx_import_preview(
            file_bytes=b"not a real docx",
            filename="safe-broken.docx",
            file_size_bytes=15,
            context_options=context_options,
        )

    stored = isolated_usage_ledger_repository.get_entry_by_request_id("request_import_failed")

    assert stored is not None
    assert stored.operation == "document_import"
    assert stored.document_operation == "import_preview"
    assert stored.status == "failed"
    assert stored.error_code == "document_import_failed"
    assert stored.error_message_safe == "无法解析 DOCX 文档，请确认文件格式正确。"
    assert_metadata_has_no_document_body(stored.metadata_json)


def test_txt_export_success_writes_usage_ledger(
    isolated_usage_ledger_repository: SQLiteUsageLedgerRepository,
) -> None:
    input_data = DocumentExportInput(
        project_title="测试短剧：灯火归来",
        document_type="short_drama_script",
        content_text=SAFE_EXPORT_TEXT,
        export_format="txt",
        context_options={
            "project_id": "project_export_txt",
            "session_id": "session_export_txt",
            "request_id": "request_export_txt",
            "source_stage": "export",
        },
    )

    output = export_document(input_data)
    stored = isolated_usage_ledger_repository.get_entry_by_request_id("request_export_txt")

    assert output.export_format == "txt"
    assert stored is not None
    assert stored.operation == "document_export"
    assert stored.document_operation == "export_txt"
    assert stored.status == "success"
    assert stored.project_id == "project_export_txt"
    assert stored.session_id == "session_export_txt"
    assert stored.output_character_count == len(output.content_text or "")
    assert_metadata_has_no_document_body(stored.metadata_json)


def test_json_export_success_writes_usage_ledger(
    isolated_usage_ledger_repository: SQLiteUsageLedgerRepository,
) -> None:
    input_data = DocumentExportInput(
        project_title="测试短剧：灯火归来",
        document_type="short_drama_script",
        structured_payload={
            "project_title": "测试短剧：灯火归来",
            "characters": [{"name": "林灯"}],
            "episodes": [{"episode_number": 1, "title": "灯火重启"}],
        },
        export_format="json",
        context_options={
            "project_id": "project_export_json",
            "session_id": "session_export_json",
            "request_id": "request_export_json",
            "source_stage": "export",
        },
    )

    output = export_document(input_data)
    stored = isolated_usage_ledger_repository.get_entry_by_request_id("request_export_json")

    assert output.export_format == "json"
    assert stored is not None
    assert stored.operation == "document_export"
    assert stored.document_operation == "export_json"
    assert stored.status == "success"
    assert stored.output_character_count == len(output.content_text or "")
    assert stored.metadata_json is not None
    assert '"characters_count": 1' in stored.metadata_json
    assert '"episode_count": 1' in stored.metadata_json
    assert "林灯" not in stored.metadata_json
    assert "灯火重启" not in stored.metadata_json


def test_docx_export_success_writes_usage_ledger(
    isolated_usage_ledger_repository: SQLiteUsageLedgerRepository,
) -> None:
    input_data = DocumentExportInput(
        project_title="测试短剧：灯火归来",
        document_type="short_drama_script",
        structured_payload={
            "project_title": "测试短剧：灯火归来",
            "logline": "年轻编剧回到旧楼。",
            "characters": [{"name": "林灯"}],
            "episodes": [{"episode_number": 1, "title": "灯火重启"}],
        },
        export_format="docx",
        context_options={
            "project_id": "project_export_docx",
            "session_id": "session_export_docx",
            "request_id": "request_export_docx",
            "source_stage": "export",
        },
    )

    docx_bytes = build_docx_export_bytes(input_data)
    stored = isolated_usage_ledger_repository.get_entry_by_request_id("request_export_docx")

    assert len(docx_bytes) > 0
    assert stored is not None
    assert stored.operation == "document_export"
    assert stored.document_operation == "export_docx"
    assert stored.status == "success"
    assert stored.project_id == "project_export_docx"
    assert stored.session_id == "session_export_docx"
    assert stored.output_character_count is None
    assert stored.metadata_json is not None
    assert '"file_size_bytes":' in stored.metadata_json
    assert "林灯" not in stored.metadata_json
    assert "灯火重启" not in stored.metadata_json


def test_unsupported_export_format_writes_safe_failed_usage_ledger(
    isolated_usage_ledger_repository: SQLiteUsageLedgerRepository,
) -> None:
    input_data = DocumentExportInput(
        project_title="测试短剧：灯火归来",
        content_text=SAFE_EXPORT_TEXT,
        export_format="docx",
        context_options={
            "request_id": "request_export_unsupported",
            "project_id": "project_export_unsupported",
        },
    )

    with pytest.raises(ValueError):
        export_document(input_data)

    stored = isolated_usage_ledger_repository.get_entry_by_request_id("request_export_unsupported")

    assert stored is not None
    assert stored.operation == "document_export"
    assert stored.document_operation == "export_docx"
    assert stored.status == "failed"
    assert stored.error_code == "unsupported_export_format"
    assert stored.error_message_safe == "DOCX export is not implemented yet."
    assert_metadata_has_no_document_body(stored.metadata_json)
