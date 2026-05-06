from pathlib import Path
import sys

import pytest


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.repositories.ownership_repository import (  # noqa: E402
    CreativeSessionRecord,
    DocumentRecord,
    ProjectRecord,
    SQLiteOwnershipRepository,
)
from app.schemas.context import ContextOptions  # noqa: E402
from app.services.ownership_service import (  # noqa: E402
    OwnershipError,
    configure_ownership_repository_for_testing,
    ensure_project_and_session,
    get_document_for_context,
    reset_ownership_repository_for_testing,
)


NOW = "2026-05-06T00:00:00+00:00"
SAFE_ERROR_FORBIDDEN_TEXT = [
    "安全测试项目",
    "完整正文",
    "source_text",
    "extracted_text",
    "preview_text",
    "content_text",
    "docx_bytes",
    "provider_raw_response",
    "api_key",
    "password",
    "password_hash",
    "access_token",
    "session_token",
    "/Users/",
    ".sqlite",
    ".db",
]


@pytest.fixture(autouse=True)
def isolated_ownership_repository(tmp_path: Path):
    repository = SQLiteOwnershipRepository(tmp_path / "ownership_guardrails.sqlite")
    configure_ownership_repository_for_testing(repository)
    yield repository
    reset_ownership_repository_for_testing()


def assert_safe_ownership_error(error: OwnershipError) -> None:
    message = str(error)
    assert message
    for forbidden in SAFE_ERROR_FORBIDDEN_TEXT:
        assert forbidden not in message


def create_project(
    repository: SQLiteOwnershipRepository,
    *,
    project_id: str,
    workspace_id: str = "workspace_a",
    owner_user_id: str = "user_a",
) -> ProjectRecord:
    return repository.create_project(
        ProjectRecord(
            id=project_id,
            workspace_id=workspace_id,
            owner_user_id=owner_user_id,
            title="安全测试项目",
            source_mode="idea",
            status="active",
            created_at=NOW,
            updated_at=NOW,
            last_active_at=NOW,
            metadata_json='{"source_mode":"idea","episode_count":3}',
        )
    )


def create_session(
    repository: SQLiteOwnershipRepository,
    *,
    session_id: str,
    project_id: str,
    workspace_id: str = "workspace_a",
    user_id: str = "user_a",
) -> CreativeSessionRecord:
    return repository.create_session(
        CreativeSessionRecord(
            id=session_id,
            project_id=project_id,
            workspace_id=workspace_id,
            user_id=user_id,
            source_mode="idea",
            context_policy="current_project_only",
            status="active",
            created_at=NOW,
            updated_at=NOW,
            last_event_at=NOW,
            metadata_json='{"context_policy":"current_project_only"}',
        )
    )


def create_document(
    repository: SQLiteOwnershipRepository,
    *,
    document_id: str,
    project_id: str,
    session_id: str,
    workspace_id: str = "workspace_a",
    user_id: str = "user_a",
) -> DocumentRecord:
    return repository.create_document(
        DocumentRecord(
            id=document_id,
            project_id=project_id,
            session_id=session_id,
            workspace_id=workspace_id,
            user_id=user_id,
            document_type="short_drama_script",
            source_stage="export",
            direction="export",
            filename_safe="safe-export.docx",
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            file_size_bytes=2048,
            character_count=None,
            export_format="docx",
            status="exported",
            created_at=NOW,
            metadata_json='{"export_format":"docx","episode_count":3}',
        )
    )


def test_project_workspace_mismatch_is_rejected(
    isolated_ownership_repository: SQLiteOwnershipRepository,
) -> None:
    create_project(isolated_ownership_repository, project_id="project_a", workspace_id="workspace_a")
    create_session(
        isolated_ownership_repository,
        session_id="session_a",
        project_id="project_a",
        workspace_id="workspace_a",
    )

    with pytest.raises(OwnershipError) as error:
        ensure_project_and_session(
            ContextOptions(
                user_id="user_a",
                workspace_id="workspace_b",
                project_id="project_a",
                session_id="session_a",
                context_policy="current_project_only",
            )
        )

    assert str(error.value) == "Project does not belong to the requested workspace."
    assert_safe_ownership_error(error.value)


def test_session_project_mismatch_is_rejected(
    isolated_ownership_repository: SQLiteOwnershipRepository,
) -> None:
    create_project(isolated_ownership_repository, project_id="project_a")
    create_project(isolated_ownership_repository, project_id="project_b")
    create_session(isolated_ownership_repository, session_id="session_x", project_id="project_b")

    with pytest.raises(OwnershipError) as error:
        ensure_project_and_session(
            ContextOptions(
                user_id="user_a",
                workspace_id="workspace_a",
                project_id="project_a",
                session_id="session_x",
                context_policy="current_project_only",
            )
        )

    assert str(error.value) == "Session does not belong to the requested project."
    assert_safe_ownership_error(error.value)


def test_session_workspace_mismatch_is_rejected(
    isolated_ownership_repository: SQLiteOwnershipRepository,
) -> None:
    create_project(isolated_ownership_repository, project_id="project_a", workspace_id="workspace_a")
    create_session(
        isolated_ownership_repository,
        session_id="session_x",
        project_id="project_a",
        workspace_id="workspace_b",
    )

    with pytest.raises(OwnershipError) as error:
        ensure_project_and_session(
            ContextOptions(
                user_id="user_a",
                workspace_id="workspace_a",
                project_id="project_a",
                session_id="session_x",
                context_policy="current_project_only",
            )
        )

    assert str(error.value) == "Session does not belong to the requested workspace."
    assert_safe_ownership_error(error.value)


def test_document_project_mismatch_is_rejected(
    isolated_ownership_repository: SQLiteOwnershipRepository,
) -> None:
    create_project(isolated_ownership_repository, project_id="project_a")
    create_project(isolated_ownership_repository, project_id="project_b")
    create_session(isolated_ownership_repository, session_id="session_a", project_id="project_a")
    create_session(isolated_ownership_repository, session_id="session_b", project_id="project_b")
    create_document(
        isolated_ownership_repository,
        document_id="document_a",
        project_id="project_a",
        session_id="session_a",
    )

    with pytest.raises(OwnershipError) as error:
        get_document_for_context(
            "document_a",
            ContextOptions(
                user_id="user_a",
                workspace_id="workspace_a",
                project_id="project_b",
                session_id="session_b",
                context_policy="current_project_only",
            ),
        )

    assert str(error.value) == "Document is not available for the requested context."
    assert_safe_ownership_error(error.value)


def test_document_session_mismatch_is_rejected(
    isolated_ownership_repository: SQLiteOwnershipRepository,
) -> None:
    create_project(isolated_ownership_repository, project_id="project_a")
    create_session(isolated_ownership_repository, session_id="session_a", project_id="project_a")
    create_session(isolated_ownership_repository, session_id="session_b", project_id="project_a")
    create_document(
        isolated_ownership_repository,
        document_id="document_a",
        project_id="project_a",
        session_id="session_a",
    )

    with pytest.raises(OwnershipError) as error:
        get_document_for_context(
            "document_a",
            ContextOptions(
                user_id="user_a",
                workspace_id="workspace_a",
                project_id="project_a",
                session_id="session_b",
                context_policy="current_project_only",
            ),
        )

    assert_safe_ownership_error(error.value)


def test_document_workspace_mismatch_is_rejected(
    isolated_ownership_repository: SQLiteOwnershipRepository,
) -> None:
    create_project(isolated_ownership_repository, project_id="project_a", workspace_id="workspace_a")
    create_session(
        isolated_ownership_repository,
        session_id="session_a",
        project_id="project_a",
        workspace_id="workspace_a",
    )
    create_document(
        isolated_ownership_repository,
        document_id="document_a",
        project_id="project_a",
        session_id="session_a",
        workspace_id="workspace_a",
    )

    with pytest.raises(OwnershipError) as error:
        get_document_for_context(
            "document_a",
            ContextOptions(
                user_id="user_a",
                workspace_id="workspace_b",
                project_id="project_a",
                session_id="session_a",
                context_policy="current_project_only",
            ),
        )

    assert_safe_ownership_error(error.value)


def test_current_project_only_rejects_cross_project_document_access(
    isolated_ownership_repository: SQLiteOwnershipRepository,
) -> None:
    create_project(isolated_ownership_repository, project_id="project_a")
    create_project(isolated_ownership_repository, project_id="project_b")
    create_session(isolated_ownership_repository, session_id="session_a", project_id="project_a")
    create_session(isolated_ownership_repository, session_id="session_b", project_id="project_b")
    create_document(
        isolated_ownership_repository,
        document_id="document_a",
        project_id="project_a",
        session_id="session_a",
    )

    with pytest.raises(OwnershipError) as error:
        get_document_for_context(
            "document_a",
            ContextOptions(
                user_id="user_a",
                workspace_id="workspace_a",
                project_id="project_b",
                session_id="session_b",
                context_policy="current_project_only",
            ),
        )

    assert_safe_ownership_error(error.value)


def test_document_access_succeeds_when_context_matches(
    isolated_ownership_repository: SQLiteOwnershipRepository,
) -> None:
    create_project(isolated_ownership_repository, project_id="project_a")
    create_session(isolated_ownership_repository, session_id="session_a", project_id="project_a")
    create_document(
        isolated_ownership_repository,
        document_id="document_a",
        project_id="project_a",
        session_id="session_a",
    )

    document = get_document_for_context(
        "document_a",
        ContextOptions(
            user_id="user_a",
            workspace_id="workspace_a",
            project_id="project_a",
            session_id="session_a",
            context_policy="current_project_only",
        ),
    )

    assert document.id == "document_a"
    assert document.project_id == "project_a"
    assert document.session_id == "session_a"
