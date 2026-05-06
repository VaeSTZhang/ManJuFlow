from pathlib import Path
import sqlite3
import sys


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.repositories.ownership_repository import (  # noqa: E402
    CreativeSessionRecord,
    DocumentRecord,
    ProjectRecord,
    SQLiteOwnershipRepository,
)


SAFE_METADATA_JSON = '{"source_mode": "idea", "episode_count": 3}'
FORBIDDEN_OWNERSHIP_CONTENT = [
    "source_text",
    "extracted_text",
    "preview_text",
    "full_response",
    "provider_raw_response",
    "api_key",
    "password",
    "password_hash",
    "access_token",
    "session_token",
    "/Users/",
]


def make_repository(tmp_path: Path) -> SQLiteOwnershipRepository:
    repository = SQLiteOwnershipRepository(tmp_path / "ownership_test.sqlite")
    repository.init_schema()
    return repository


def build_project_record(**overrides) -> ProjectRecord:
    data = {
        "id": "project_safe_001",
        "workspace_id": "workspace_dramora_internal",
        "owner_user_id": "user_safe_creator_001",
        "title": "测试短剧：旧楼灯火",
        "source_mode": "idea",
        "status": "active",
        "created_at": "2026-05-06T00:00:00+00:00",
        "updated_at": "2026-05-06T00:00:00+00:00",
        "last_active_at": None,
        "metadata_json": SAFE_METADATA_JSON,
    }
    data.update(overrides)
    return ProjectRecord(**data)


def build_session_record(**overrides) -> CreativeSessionRecord:
    data = {
        "id": "session_safe_001",
        "project_id": "project_safe_001",
        "workspace_id": "workspace_dramora_internal",
        "user_id": "user_safe_creator_001",
        "source_mode": "idea",
        "context_policy": "current_project_only",
        "status": "active",
        "created_at": "2026-05-06T00:10:00+00:00",
        "updated_at": "2026-05-06T00:10:00+00:00",
        "last_event_at": None,
        "metadata_json": SAFE_METADATA_JSON,
    }
    data.update(overrides)
    return CreativeSessionRecord(**data)


def build_document_record(**overrides) -> DocumentRecord:
    data = {
        "id": "document_safe_001",
        "project_id": "project_safe_001",
        "session_id": "session_safe_001",
        "workspace_id": "workspace_dramora_internal",
        "user_id": "user_safe_creator_001",
        "document_type": "source_script",
        "source_stage": "imported_document",
        "direction": "import",
        "filename_safe": "safe-source.docx",
        "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "file_size_bytes": 2048,
        "character_count": 120,
        "export_format": None,
        "status": "preview_ready",
        "created_at": "2026-05-06T00:20:00+00:00",
        "metadata_json": '{"paragraph_count": 3, "has_detected_title": true}',
    }
    data.update(overrides)
    return DocumentRecord(**data)


def assert_metadata_json_is_safe(metadata_json: str | None) -> None:
    assert metadata_json is not None
    for forbidden in FORBIDDEN_OWNERSHIP_CONTENT:
        assert forbidden not in metadata_json


def test_init_schema_creates_three_tables(tmp_path: Path) -> None:
    database_path = tmp_path / "ownership_test.sqlite"
    repository = SQLiteOwnershipRepository(database_path)

    repository.init_schema()
    repository.init_schema()

    with sqlite3.connect(database_path) as connection:
        table_names = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }

    assert {"projects", "creative_sessions", "documents"}.issubset(table_names)


def test_create_project_and_get_project(tmp_path: Path) -> None:
    repository = make_repository(tmp_path)
    record = build_project_record()

    repository.create_project(record)
    fetched = repository.get_project("project_safe_001")

    assert fetched == record
    assert fetched is not None
    assert_metadata_json_is_safe(fetched.metadata_json)


def test_get_project_returns_none_for_missing_project(tmp_path: Path) -> None:
    repository = make_repository(tmp_path)

    assert repository.get_project("missing_project") is None
    assert repository.get_project(" ") is None


def test_list_projects_filters_by_workspace_id(tmp_path: Path) -> None:
    repository = make_repository(tmp_path)
    repository.create_project(build_project_record(id="project_internal"))
    repository.create_project(
        build_project_record(
            id="project_other_workspace",
            workspace_id="workspace_safe_other",
        )
    )

    projects = repository.list_projects(workspace_id="workspace_dramora_internal")

    assert [project.id for project in projects] == ["project_internal"]


def test_list_projects_filters_by_owner_user_id(tmp_path: Path) -> None:
    repository = make_repository(tmp_path)
    repository.create_project(build_project_record(id="project_creator"))
    repository.create_project(
        build_project_record(
            id="project_reviewer",
            owner_user_id="user_safe_reviewer_001",
        )
    )

    projects = repository.list_projects(owner_user_id="user_safe_creator_001")

    assert [project.id for project in projects] == ["project_creator"]


def test_list_projects_limit_is_applied(tmp_path: Path) -> None:
    repository = make_repository(tmp_path)
    repository.create_project(build_project_record(id="project_001"))
    repository.create_project(build_project_record(id="project_002"))

    projects = repository.list_projects(limit=1)

    assert len(projects) == 1


def test_create_session_and_get_session(tmp_path: Path) -> None:
    repository = make_repository(tmp_path)
    record = build_session_record()

    repository.create_session(record)
    fetched = repository.get_session("session_safe_001")

    assert fetched == record
    assert fetched is not None
    assert fetched.context_policy == "current_project_only"
    assert_metadata_json_is_safe(fetched.metadata_json)


def test_list_sessions_filters_by_project_id(tmp_path: Path) -> None:
    repository = make_repository(tmp_path)
    repository.create_session(build_session_record(id="session_project_001"))
    repository.create_session(
        build_session_record(
            id="session_project_002",
            project_id="project_safe_002",
        )
    )

    sessions = repository.list_sessions(project_id="project_safe_001")

    assert [session.id for session in sessions] == ["session_project_001"]


def test_list_sessions_filters_by_user_id(tmp_path: Path) -> None:
    repository = make_repository(tmp_path)
    repository.create_session(build_session_record(id="session_creator"))
    repository.create_session(
        build_session_record(
            id="session_reviewer",
            user_id="user_safe_reviewer_001",
        )
    )

    sessions = repository.list_sessions(user_id="user_safe_creator_001")

    assert [session.id for session in sessions] == ["session_creator"]


def test_session_belongs_to_project_returns_true_or_false(tmp_path: Path) -> None:
    repository = make_repository(tmp_path)
    repository.create_session(build_session_record())

    assert repository.session_belongs_to_project("session_safe_001", "project_safe_001") is True
    assert repository.session_belongs_to_project("session_safe_001", "project_other") is False
    assert repository.session_belongs_to_project("session_missing", "project_safe_001") is False


def test_create_document_and_get_document(tmp_path: Path) -> None:
    repository = make_repository(tmp_path)
    record = build_document_record()

    repository.create_document(record)
    fetched = repository.get_document("document_safe_001")

    assert fetched == record
    assert fetched is not None
    assert fetched.direction == "import"
    assert_metadata_json_is_safe(fetched.metadata_json)


def test_list_documents_filters_by_project_id(tmp_path: Path) -> None:
    repository = make_repository(tmp_path)
    repository.create_document(build_document_record(id="document_project_001"))
    repository.create_document(
        build_document_record(
            id="document_project_002",
            project_id="project_safe_002",
        )
    )

    documents = repository.list_documents(project_id="project_safe_001")

    assert [document.id for document in documents] == ["document_project_001"]


def test_list_documents_filters_by_session_id(tmp_path: Path) -> None:
    repository = make_repository(tmp_path)
    repository.create_document(build_document_record(id="document_session_001"))
    repository.create_document(
        build_document_record(
            id="document_session_002",
            session_id="session_safe_002",
        )
    )

    documents = repository.list_documents(session_id="session_safe_001")

    assert [document.id for document in documents] == ["document_session_001"]


def test_list_documents_filters_by_user_id(tmp_path: Path) -> None:
    repository = make_repository(tmp_path)
    repository.create_document(build_document_record(id="document_creator"))
    repository.create_document(
        build_document_record(
            id="document_reviewer",
            user_id="user_safe_reviewer_001",
        )
    )

    documents = repository.list_documents(user_id="user_safe_creator_001")

    assert [document.id for document in documents] == ["document_creator"]


def test_document_belongs_to_project_returns_true_or_false(tmp_path: Path) -> None:
    repository = make_repository(tmp_path)
    repository.create_document(build_document_record())

    assert repository.document_belongs_to_project("document_safe_001", "project_safe_001") is True
    assert repository.document_belongs_to_project("document_safe_001", "project_other") is False
    assert repository.document_belongs_to_project("document_missing", "project_safe_001") is False


def test_document_belongs_to_session_returns_true_or_false(tmp_path: Path) -> None:
    repository = make_repository(tmp_path)
    repository.create_document(build_document_record())

    assert repository.document_belongs_to_session("document_safe_001", "session_safe_001") is True
    assert repository.document_belongs_to_session("document_safe_001", "session_other") is False
    assert repository.document_belongs_to_session("document_missing", "session_safe_001") is False


def test_import_and_export_documents_can_be_recorded(tmp_path: Path) -> None:
    repository = make_repository(tmp_path)
    import_document = build_document_record(
        id="document_import_001",
        direction="import",
        document_type="source_script",
        source_stage="imported_document",
        status="preview_ready",
    )
    export_document = build_document_record(
        id="document_export_001",
        direction="export",
        document_type="short_drama_script",
        source_stage="export",
        filename_safe="safe-export.docx",
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        export_format="docx",
        status="exported",
        metadata_json='{"export_format": "docx", "episode_count": 3}',
    )

    repository.create_document(import_document)
    repository.create_document(export_document)

    documents = repository.list_documents(project_id="project_safe_001", limit=10)
    document_by_id = {document.id: document for document in documents}

    assert document_by_id["document_import_001"].direction == "import"
    assert document_by_id["document_export_001"].direction == "export"
    assert document_by_id["document_export_001"].export_format == "docx"
    assert_metadata_json_is_safe(document_by_id["document_import_001"].metadata_json)
    assert_metadata_json_is_safe(document_by_id["document_export_001"].metadata_json)


def test_metadata_json_samples_do_not_contain_sensitive_content() -> None:
    for metadata_json in [
        SAFE_METADATA_JSON,
        '{"paragraph_count": 3, "has_detected_title": true}',
        '{"export_format": "docx", "episode_count": 3}',
    ]:
        assert_metadata_json_is_safe(metadata_json)


def test_repository_tests_use_tmp_path(tmp_path: Path) -> None:
    repository = make_repository(tmp_path)
    repository.create_project(build_project_record())
    repository.create_session(build_session_record())
    repository.create_document(build_document_record())

    assert (tmp_path / "ownership_test.sqlite").exists()
    assert not Path("ownership_test.sqlite").exists()
