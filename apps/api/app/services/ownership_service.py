from datetime import UTC, datetime
import json
import os
from pathlib import Path
from uuid import uuid4

from app.repositories.ownership_repository import (
    CreativeSessionRecord,
    DocumentRecord,
    ProjectRecord,
    SQLiteOwnershipRepository,
)
from app.schemas.context import ContextOptions


OWNERSHIP_DB_PATH_ENV_VAR = "DRAMORA_OWNERSHIP_DB_PATH"
DEFAULT_OWNERSHIP_DB_PATH = Path(".local") / "dramora_ownership.sqlite3"
DEFAULT_USER_ID = "user_safe_creator_001"
DEFAULT_WORKSPACE_ID = "workspace_dramora_internal"
DEFAULT_PROJECT_ID = "project_creation_default"
DEFAULT_SESSION_ID = "session_creation_default"
DEFAULT_CONTEXT_POLICY = "current_project_only"

_ownership_repository_override: SQLiteOwnershipRepository | None = None
_default_ownership_repository: SQLiteOwnershipRepository | None = None


class OwnershipError(ValueError):
    pass


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def get_default_ownership_database_path() -> Path:
    configured_path = os.getenv(OWNERSHIP_DB_PATH_ENV_VAR)
    if configured_path:
        return Path(configured_path)
    return DEFAULT_OWNERSHIP_DB_PATH


def get_ownership_repository() -> SQLiteOwnershipRepository:
    if _ownership_repository_override is not None:
        return _ownership_repository_override

    global _default_ownership_repository
    if _default_ownership_repository is None:
        database_path = get_default_ownership_database_path()
        database_path.parent.mkdir(parents=True, exist_ok=True)
        _default_ownership_repository = SQLiteOwnershipRepository(database_path)
        _default_ownership_repository.init_schema()

    return _default_ownership_repository


def configure_ownership_repository_for_testing(repository: SQLiteOwnershipRepository) -> None:
    global _ownership_repository_override
    repository.init_schema()
    _ownership_repository_override = repository


def reset_ownership_repository_for_testing() -> None:
    global _ownership_repository_override
    _ownership_repository_override = None


def ensure_project_and_session(
    context_options: ContextOptions | None,
    *,
    project_title: str | None = None,
    source_mode: str | None = None,
) -> tuple[ProjectRecord, CreativeSessionRecord]:
    context = _resolve_context(context_options)
    repository = get_ownership_repository()
    now = _utc_now_iso()

    project = repository.get_project(context["project_id"])
    if project is None:
        project = repository.create_project(
            ProjectRecord(
                id=context["project_id"],
                workspace_id=context["workspace_id"],
                owner_user_id=context["user_id"],
                title=project_title or context["project_id"],
                source_mode=source_mode,
                status="active",
                created_at=now,
                updated_at=now,
                last_active_at=now,
                metadata_json=_safe_json(
                    {
                        "source_mode": source_mode,
                        "has_project_title": bool(project_title),
                    }
                ),
            )
        )
    elif project.workspace_id != context["workspace_id"]:
        raise OwnershipError("Project does not belong to the requested workspace.")

    session = repository.get_session(context["session_id"])
    if session is None:
        session = repository.create_session(
            CreativeSessionRecord(
                id=context["session_id"],
                project_id=project.id,
                workspace_id=project.workspace_id,
                user_id=context["user_id"],
                source_mode=source_mode,
                context_policy=context["context_policy"],
                status="active",
                created_at=now,
                updated_at=now,
                last_event_at=now,
                metadata_json=_safe_json(
                    {
                        "source_mode": source_mode,
                        "context_policy": context["context_policy"],
                    }
                ),
            )
        )
    elif session.project_id != project.id:
        raise OwnershipError("Session does not belong to the requested project.")
    elif session.workspace_id != project.workspace_id:
        raise OwnershipError("Session does not belong to the requested workspace.")

    return project, session


def build_ownership_metadata(
    project: ProjectRecord,
    session: CreativeSessionRecord,
) -> dict[str, str]:
    return {
        "project_id": project.id,
        "session_id": session.id,
        "workspace_id": project.workspace_id,
        "context_policy": session.context_policy,
    }


def get_document_for_context(
    document_id: str,
    context_options: ContextOptions | None,
) -> DocumentRecord:
    context = _resolve_context(context_options)
    document = get_ownership_repository().get_document(document_id)
    if document is None:
        raise OwnershipError("Document is not available for the requested context.")
    if document.workspace_id != context["workspace_id"]:
        raise OwnershipError("Document is not available for the requested context.")
    if document.project_id != context["project_id"]:
        raise OwnershipError("Document is not available for the requested context.")
    if document.session_id != context["session_id"]:
        raise OwnershipError("Document is not available for the requested context.")
    if document.user_id != context["user_id"]:
        raise OwnershipError("Document is not available for the requested context.")
    return document


def record_import_document_ownership(
    *,
    context_options: ContextOptions | None,
    project_title: str | None,
    source_mode: str | None,
    filename_safe: str | None,
    content_type: str | None,
    file_size_bytes: int | None,
    character_count: int | None,
    paragraph_count: int | None,
    source_type: str | None,
    has_detected_title: bool,
) -> DocumentRecord:
    project, session = ensure_project_and_session(
        context_options,
        project_title=project_title,
        source_mode=source_mode,
    )
    now = _utc_now_iso()
    return get_ownership_repository().create_document(
        DocumentRecord(
            id=_document_id("import"),
            project_id=project.id,
            session_id=session.id,
            workspace_id=project.workspace_id,
            user_id=session.user_id,
            document_type="source_script",
            source_stage=(
                context_options.source_stage
                if context_options and context_options.source_stage
                else "imported_document"
            ),
            direction="import",
            filename_safe=filename_safe,
            content_type=content_type,
            file_size_bytes=file_size_bytes,
            character_count=character_count,
            export_format=None,
            status="preview_ready",
            created_at=now,
            metadata_json=_safe_json(
                {
                    "paragraph_count": paragraph_count,
                    "source_type": source_type,
                    "has_detected_title": has_detected_title,
                }
            ),
        )
    )


def record_export_document_ownership(
    *,
    context_options: ContextOptions | None,
    project_title: str | None,
    source_mode: str | None,
    document_type: str,
    source_stage: str,
    export_format: str,
    filename_safe: str | None,
    content_type: str | None,
    file_size_bytes: int | None,
    character_count: int | None,
    episode_count: int | None,
    characters_count: int | None,
) -> DocumentRecord:
    project, session = ensure_project_and_session(
        context_options,
        project_title=project_title,
        source_mode=source_mode,
    )
    now = _utc_now_iso()
    return get_ownership_repository().create_document(
        DocumentRecord(
            id=_document_id(f"export_{export_format}"),
            project_id=project.id,
            session_id=session.id,
            workspace_id=project.workspace_id,
            user_id=session.user_id,
            document_type=document_type,
            source_stage=context_options.source_stage if context_options and context_options.source_stage else source_stage,
            direction="export",
            filename_safe=filename_safe,
            content_type=content_type,
            file_size_bytes=file_size_bytes,
            character_count=character_count,
            export_format=export_format,
            status="exported",
            created_at=now,
            metadata_json=_safe_json(
                {
                    "export_format": export_format,
                    "document_type": document_type,
                    "episode_count": episode_count,
                    "characters_count": characters_count,
                }
            ),
        )
    )


def _resolve_context(context_options: ContextOptions | None) -> dict[str, str]:
    return {
        "user_id": context_options.user_id if context_options and context_options.user_id else DEFAULT_USER_ID,
        "workspace_id": context_options.workspace_id if context_options and context_options.workspace_id else DEFAULT_WORKSPACE_ID,
        "project_id": context_options.project_id if context_options and context_options.project_id else DEFAULT_PROJECT_ID,
        "session_id": context_options.session_id if context_options and context_options.session_id else DEFAULT_SESSION_ID,
        "context_policy": (
            context_options.context_policy
            if context_options and context_options.context_policy
            else DEFAULT_CONTEXT_POLICY
        ),
    }


def _safe_json(payload: dict[str, str | int | bool | None]) -> str:
    return json.dumps(
        {key: value for key, value in payload.items() if value is not None},
        ensure_ascii=False,
        sort_keys=True,
    )


def _document_id(prefix: str) -> str:
    return f"document_{prefix}_{uuid4().hex}"
