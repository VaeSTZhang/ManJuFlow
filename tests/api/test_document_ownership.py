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
from app.services.document_import_service import build_document_import_preview  # noqa: E402
from app.services.ownership_service import (  # noqa: E402
    configure_ownership_repository_for_testing,
    get_ownership_repository,
    reset_ownership_repository_for_testing,
)
from app.services.usage_ledger_service import (  # noqa: E402
    configure_usage_ledger_repository_for_testing,
    reset_usage_ledger_repository_for_testing,
)


SAFE_IMPORT_TEXT = "旧影院来信\n放映员收到一封写给未来的信。"
SAFE_EXPORT_TEXT = "第一集：林灯回到旧楼，发现父亲留下的剧本。"


@pytest.fixture(autouse=True)
def isolated_repositories(tmp_path: Path):
    usage_repository = SQLiteUsageLedgerRepository(tmp_path / "document_ownership_usage.sqlite")
    ownership_repository = SQLiteOwnershipRepository(tmp_path / "document_ownership_test.sqlite")
    configure_usage_ledger_repository_for_testing(usage_repository)
    configure_ownership_repository_for_testing(ownership_repository)
    yield ownership_repository
    reset_usage_ledger_repository_for_testing()
    reset_ownership_repository_for_testing()


def assert_document_metadata_is_safe(metadata_json: str | None) -> None:
    assert metadata_json is not None
    assert SAFE_IMPORT_TEXT not in metadata_json
    assert SAFE_EXPORT_TEXT not in metadata_json
    assert "extracted_text" not in metadata_json
    assert "preview_text" not in metadata_json
    assert "content_text" not in metadata_json
    assert "docx_bytes" not in metadata_json
    assert "api_key" not in metadata_json
    assert "password" not in metadata_json
    assert "access_token" not in metadata_json
    assert "/Users/" not in metadata_json


def test_import_preview_creates_import_document_ownership() -> None:
    build_document_import_preview(
        filename="/Users/example/private/old-cinema.docx",
        extracted_text=SAFE_IMPORT_TEXT,
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        file_size_bytes=4096,
        project_title="测试短剧：旧影院来信",
        context_options=ContextOptions(
            user_id="user_doc_import",
            workspace_id="workspace_doc",
            project_id="project_doc_import",
            session_id="session_doc_import",
            source_stage="imported_document",
        ),
    )
    documents = get_ownership_repository().list_documents(project_id="project_doc_import")

    assert len(documents) == 1
    document = documents[0]
    assert document.direction == "import"
    assert document.document_type == "source_script"
    assert document.source_stage == "imported_document"
    assert document.filename_safe == "old-cinema.docx"
    assert document.character_count == len(SAFE_IMPORT_TEXT)
    assert document_belongs_to_context(document.project_id, document.session_id)
    assert_document_metadata_is_safe(document.metadata_json)


def test_txt_export_creates_export_document_ownership() -> None:
    export_document(
        DocumentExportInput(
            project_title="测试短剧：灯火归来",
            document_type="short_drama_script",
            content_text=SAFE_EXPORT_TEXT,
            export_format="txt",
            context_options={
                "project_id": "project_doc_export_txt",
                "session_id": "session_doc_export_txt",
                "source_stage": "export",
            },
        )
    )
    documents = get_ownership_repository().list_documents(project_id="project_doc_export_txt")

    assert len(documents) == 1
    document = documents[0]
    assert document.direction == "export"
    assert document.export_format == "txt"
    assert document.document_type == "short_drama_script"
    assert document.character_count is not None
    assert document.character_count > 0
    assert_document_metadata_is_safe(document.metadata_json)


def test_json_export_creates_export_document_ownership() -> None:
    export_document(
        DocumentExportInput(
            project_title="测试短剧：灯火归来",
            document_type="short_drama_script",
            structured_payload={
                "project_title": "测试短剧：灯火归来",
                "source_mode": "idea",
                "characters": [{"name": "林灯"}],
                "episodes": [{"episode_number": 1, "title": "灯火重启"}],
            },
            export_format="json",
            context_options={
                "project_id": "project_doc_export_json",
                "session_id": "session_doc_export_json",
                "source_stage": "export",
            },
        )
    )
    document = get_ownership_repository().list_documents(project_id="project_doc_export_json")[0]

    assert document.direction == "export"
    assert document.export_format == "json"
    assert document.metadata_json is not None
    assert '"episode_count": 1' in document.metadata_json
    assert '"characters_count": 1' in document.metadata_json
    assert "林灯" not in document.metadata_json
    assert "灯火重启" not in document.metadata_json


def test_docx_export_creates_export_document_ownership() -> None:
    docx_bytes = build_docx_export_bytes(
        DocumentExportInput(
            project_title="测试短剧：灯火归来",
            document_type="short_drama_script",
            structured_payload={
                "project_title": "测试短剧：灯火归来",
                "source_mode": "idea",
                "logline": SAFE_EXPORT_TEXT,
                "characters": [{"name": "林灯"}],
                "episodes": [{"episode_number": 1, "title": "灯火重启"}],
            },
            export_format="docx",
            context_options={
                "project_id": "project_doc_export_docx",
                "session_id": "session_doc_export_docx",
                "source_stage": "export",
            },
        )
    )
    document = get_ownership_repository().list_documents(project_id="project_doc_export_docx")[0]

    assert len(docx_bytes) > 0
    assert document.direction == "export"
    assert document.export_format == "docx"
    assert document.file_size_bytes == len(docx_bytes)
    assert document.character_count is None
    assert document.metadata_json is not None
    assert "docx_bytes" not in document.metadata_json
    assert "PK" not in document.metadata_json
    assert SAFE_EXPORT_TEXT not in document.metadata_json


def document_belongs_to_context(project_id: str, session_id: str | None) -> bool:
    if session_id is None:
        return False
    repository = get_ownership_repository()
    return repository.session_belongs_to_project(session_id, project_id)
