from pathlib import Path
import sys

import pytest


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.repositories.ownership_repository import (  # noqa: E402
    CreativeSessionRecord,
    ProjectRecord,
    SQLiteOwnershipRepository,
)
from app.schemas.context import ContextOptions  # noqa: E402
from app.services.ownership_service import (  # noqa: E402
    DEFAULT_PROJECT_ID,
    DEFAULT_SESSION_ID,
    DEFAULT_USER_ID,
    DEFAULT_WORKSPACE_ID,
    OwnershipError,
    configure_ownership_repository_for_testing,
    ensure_project_and_session,
    record_export_document_ownership,
    record_import_document_ownership,
    reset_ownership_repository_for_testing,
)


FORBIDDEN_OWNERSHIP_METADATA = [
    "source_text",
    "extracted_text",
    "preview_text",
    "content_text",
    "docx_bytes",
    "api_key",
    "password",
    "password_hash",
    "access_token",
    "session_token",
    "/Users/",
]


@pytest.fixture(autouse=True)
def isolated_ownership_repository(tmp_path: Path):
    repository = SQLiteOwnershipRepository(tmp_path / "ownership_service_test.sqlite")
    configure_ownership_repository_for_testing(repository)
    yield repository
    reset_ownership_repository_for_testing()


def assert_metadata_is_safe(metadata_json: str | None) -> None:
    assert metadata_json is not None
    for forbidden in FORBIDDEN_OWNERSHIP_METADATA:
        assert forbidden not in metadata_json


def test_ensure_project_and_session_creates_default_records_when_context_missing(
    isolated_ownership_repository: SQLiteOwnershipRepository,
) -> None:
    project, session = ensure_project_and_session(
        None,
        project_title="测试短剧：默认项目",
        source_mode="idea",
    )

    assert project.id == DEFAULT_PROJECT_ID
    assert project.workspace_id == DEFAULT_WORKSPACE_ID
    assert project.owner_user_id == DEFAULT_USER_ID
    assert project.title == "测试短剧：默认项目"
    assert session.id == DEFAULT_SESSION_ID
    assert session.project_id == DEFAULT_PROJECT_ID
    assert_metadata_is_safe(project.metadata_json)
    assert_metadata_is_safe(session.metadata_json)


def test_ensure_project_and_session_uses_context_options(
    isolated_ownership_repository: SQLiteOwnershipRepository,
) -> None:
    context = ContextOptions(
        user_id="user_safe_creator_001",
        workspace_id="workspace_dramora_internal",
        project_id="project_context_001",
        session_id="session_context_001",
        context_policy="current_project_only",
    )

    project, session = ensure_project_and_session(
        context,
        project_title="测试短剧：上下文项目",
        source_mode="film_script",
    )

    assert project.id == "project_context_001"
    assert project.workspace_id == "workspace_dramora_internal"
    assert project.owner_user_id == "user_safe_creator_001"
    assert session.id == "session_context_001"
    assert session.project_id == "project_context_001"
    assert session.context_policy == "current_project_only"


def test_repeated_ensure_does_not_duplicate_project_or_session(
    isolated_ownership_repository: SQLiteOwnershipRepository,
) -> None:
    context = ContextOptions(project_id="project_repeat", session_id="session_repeat")

    ensure_project_and_session(context, project_title="第一次标题", source_mode="idea")
    ensure_project_and_session(context, project_title="第二次标题", source_mode="novel")

    assert len(isolated_ownership_repository.list_projects()) == 1
    assert len(isolated_ownership_repository.list_sessions()) == 1
    assert isolated_ownership_repository.get_project("project_repeat").title == "第一次标题"


def test_ensure_fails_when_session_project_mismatch(
    isolated_ownership_repository: SQLiteOwnershipRepository,
) -> None:
    isolated_ownership_repository.create_project(
        ProjectRecord(
            id="project_expected",
            workspace_id="workspace_dramora_internal",
            owner_user_id="user_safe_creator_001",
            title="安全项目",
            source_mode="idea",
            status="active",
            created_at="2026-05-06T00:00:00+00:00",
            updated_at="2026-05-06T00:00:00+00:00",
            last_active_at=None,
            metadata_json='{"source_mode": "idea"}',
        )
    )
    isolated_ownership_repository.create_session(
        CreativeSessionRecord(
            id="session_mismatch",
            project_id="project_other",
            workspace_id="workspace_dramora_internal",
            user_id="user_safe_creator_001",
            source_mode="idea",
            context_policy="current_project_only",
            status="active",
            created_at="2026-05-06T00:00:00+00:00",
            updated_at="2026-05-06T00:00:00+00:00",
            last_event_at=None,
            metadata_json='{"source_mode": "idea"}',
        )
    )

    with pytest.raises(OwnershipError, match="Session does not belong"):
        ensure_project_and_session(
            ContextOptions(project_id="project_expected", session_id="session_mismatch")
        )


def test_ensure_fails_when_project_workspace_mismatch(
    isolated_ownership_repository: SQLiteOwnershipRepository,
) -> None:
    ensure_project_and_session(
        ContextOptions(
            workspace_id="workspace_dramora_internal",
            project_id="project_workspace_mismatch",
            session_id="session_workspace_mismatch",
        )
    )

    with pytest.raises(OwnershipError, match="Project does not belong"):
        ensure_project_and_session(
            ContextOptions(
                workspace_id="workspace_safe_other",
                project_id="project_workspace_mismatch",
                session_id="session_safe_other",
            )
        )


def test_record_import_document_ownership_creates_safe_document(
    isolated_ownership_repository: SQLiteOwnershipRepository,
) -> None:
    context = ContextOptions(
        project_id="project_import_ownership",
        session_id="session_import_ownership",
        source_stage="imported_document",
    )

    document = record_import_document_ownership(
        context_options=context,
        project_title="测试短剧：导入项目",
        source_mode="docx",
        filename_safe="safe-import.docx",
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        file_size_bytes=2048,
        character_count=120,
        paragraph_count=3,
        source_type="docx",
        has_detected_title=True,
    )

    assert document.direction == "import"
    assert document.project_id == "project_import_ownership"
    assert document.session_id == "session_import_ownership"
    assert document.document_type == "source_script"
    assert document.status == "preview_ready"
    assert_metadata_is_safe(document.metadata_json)


def test_record_export_document_ownership_creates_safe_document(
    isolated_ownership_repository: SQLiteOwnershipRepository,
) -> None:
    document = record_export_document_ownership(
        context_options=ContextOptions(
            project_id="project_export_ownership",
            session_id="session_export_ownership",
            source_stage="export",
        ),
        project_title="测试短剧：导出项目",
        source_mode="idea",
        document_type="short_drama_script",
        source_stage="script",
        export_format="docx",
        filename_safe="safe-export.docx",
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        file_size_bytes=4096,
        character_count=None,
        episode_count=3,
        characters_count=4,
    )

    assert document.direction == "export"
    assert document.project_id == "project_export_ownership"
    assert document.session_id == "session_export_ownership"
    assert document.document_type == "short_drama_script"
    assert document.export_format == "docx"
    assert document.status == "exported"
    assert_metadata_is_safe(document.metadata_json)


def test_tests_use_tmp_path(isolated_ownership_repository: SQLiteOwnershipRepository, tmp_path: Path) -> None:
    ensure_project_and_session(ContextOptions(project_id="project_tmp", session_id="session_tmp"))

    assert (tmp_path / "ownership_service_test.sqlite").exists()
    assert not Path("ownership_service_test.sqlite").exists()
