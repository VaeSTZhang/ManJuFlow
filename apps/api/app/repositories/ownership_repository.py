from dataclasses import dataclass
from pathlib import Path
import sqlite3


@dataclass(frozen=True)
class ProjectRecord:
    id: str
    workspace_id: str
    owner_user_id: str
    title: str
    source_mode: str | None
    status: str
    created_at: str
    updated_at: str
    last_active_at: str | None
    metadata_json: str | None


@dataclass(frozen=True)
class CreativeSessionRecord:
    id: str
    project_id: str
    workspace_id: str
    user_id: str
    source_mode: str | None
    context_policy: str
    status: str
    created_at: str
    updated_at: str
    last_event_at: str | None
    metadata_json: str | None


@dataclass(frozen=True)
class DocumentRecord:
    id: str
    project_id: str
    session_id: str | None
    workspace_id: str
    user_id: str
    document_type: str
    source_stage: str
    direction: str
    filename_safe: str | None
    content_type: str | None
    file_size_bytes: int | None
    character_count: int | None
    export_format: str | None
    status: str
    created_at: str
    metadata_json: str | None


class SQLiteOwnershipRepository:
    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)

    def init_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    workspace_id TEXT NOT NULL,
                    owner_user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    source_mode TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_active_at TEXT,
                    metadata_json TEXT
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS creative_sessions (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    workspace_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    source_mode TEXT,
                    context_policy TEXT NOT NULL DEFAULT 'current_project_only',
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_event_at TEXT,
                    metadata_json TEXT
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    session_id TEXT,
                    workspace_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    document_type TEXT NOT NULL,
                    source_stage TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    filename_safe TEXT,
                    content_type TEXT,
                    file_size_bytes INTEGER,
                    character_count INTEGER,
                    export_format TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    metadata_json TEXT
                )
                """
            )
            for table_name, index_name, column_name in [
                ("projects", "idx_projects_workspace_id", "workspace_id"),
                ("projects", "idx_projects_owner_user_id", "owner_user_id"),
                ("creative_sessions", "idx_creative_sessions_project_id", "project_id"),
                ("creative_sessions", "idx_creative_sessions_user_id", "user_id"),
                ("documents", "idx_documents_project_id", "project_id"),
                ("documents", "idx_documents_session_id", "session_id"),
                ("documents", "idx_documents_user_id", "user_id"),
                ("documents", "idx_documents_workspace_id", "workspace_id"),
            ]:
                connection.execute(
                    f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({column_name})"
                )

    def create_project(self, record: ProjectRecord) -> ProjectRecord:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO projects (
                    id,
                    workspace_id,
                    owner_user_id,
                    title,
                    source_mode,
                    status,
                    created_at,
                    updated_at,
                    last_active_at,
                    metadata_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.id,
                    record.workspace_id,
                    record.owner_user_id,
                    record.title,
                    record.source_mode,
                    record.status,
                    record.created_at,
                    record.updated_at,
                    record.last_active_at,
                    record.metadata_json,
                ),
            )
        return record

    def get_project(self, project_id: str) -> ProjectRecord | None:
        normalized_project_id = project_id.strip()
        if not normalized_project_id:
            return None
        return self._fetch_project("SELECT * FROM projects WHERE id = ?", (normalized_project_id,))

    def list_projects(
        self,
        workspace_id: str | None = None,
        owner_user_id: str | None = None,
        limit: int = 100,
    ) -> list[ProjectRecord]:
        filters: list[str] = []
        parameters: list[str | int] = []
        if workspace_id is not None:
            filters.append("workspace_id = ?")
            parameters.append(workspace_id)
        if owner_user_id is not None:
            filters.append("owner_user_id = ?")
            parameters.append(owner_user_id)
        where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
        parameters.append(max(0, limit))
        with self._connect() as connection:
            rows = connection.execute(
                f"""
                SELECT * FROM projects
                {where_clause}
                ORDER BY updated_at DESC, id DESC
                LIMIT ?
                """,
                tuple(parameters),
            ).fetchall()
        return [self._row_to_project(row) for row in rows]

    def create_session(self, record: CreativeSessionRecord) -> CreativeSessionRecord:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO creative_sessions (
                    id,
                    project_id,
                    workspace_id,
                    user_id,
                    source_mode,
                    context_policy,
                    status,
                    created_at,
                    updated_at,
                    last_event_at,
                    metadata_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.id,
                    record.project_id,
                    record.workspace_id,
                    record.user_id,
                    record.source_mode,
                    record.context_policy,
                    record.status,
                    record.created_at,
                    record.updated_at,
                    record.last_event_at,
                    record.metadata_json,
                ),
            )
        return record

    def get_session(self, session_id: str) -> CreativeSessionRecord | None:
        normalized_session_id = session_id.strip()
        if not normalized_session_id:
            return None
        return self._fetch_session("SELECT * FROM creative_sessions WHERE id = ?", (normalized_session_id,))

    def list_sessions(
        self,
        project_id: str | None = None,
        user_id: str | None = None,
        limit: int = 100,
    ) -> list[CreativeSessionRecord]:
        filters: list[str] = []
        parameters: list[str | int] = []
        if project_id is not None:
            filters.append("project_id = ?")
            parameters.append(project_id)
        if user_id is not None:
            filters.append("user_id = ?")
            parameters.append(user_id)
        where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
        parameters.append(max(0, limit))
        with self._connect() as connection:
            rows = connection.execute(
                f"""
                SELECT * FROM creative_sessions
                {where_clause}
                ORDER BY updated_at DESC, id DESC
                LIMIT ?
                """,
                tuple(parameters),
            ).fetchall()
        return [self._row_to_session(row) for row in rows]

    def create_document(self, record: DocumentRecord) -> DocumentRecord:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO documents (
                    id,
                    project_id,
                    session_id,
                    workspace_id,
                    user_id,
                    document_type,
                    source_stage,
                    direction,
                    filename_safe,
                    content_type,
                    file_size_bytes,
                    character_count,
                    export_format,
                    status,
                    created_at,
                    metadata_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.id,
                    record.project_id,
                    record.session_id,
                    record.workspace_id,
                    record.user_id,
                    record.document_type,
                    record.source_stage,
                    record.direction,
                    record.filename_safe,
                    record.content_type,
                    record.file_size_bytes,
                    record.character_count,
                    record.export_format,
                    record.status,
                    record.created_at,
                    record.metadata_json,
                ),
            )
        return record

    def get_document(self, document_id: str) -> DocumentRecord | None:
        normalized_document_id = document_id.strip()
        if not normalized_document_id:
            return None
        return self._fetch_document("SELECT * FROM documents WHERE id = ?", (normalized_document_id,))

    def list_documents(
        self,
        project_id: str | None = None,
        session_id: str | None = None,
        user_id: str | None = None,
        limit: int = 100,
    ) -> list[DocumentRecord]:
        filters: list[str] = []
        parameters: list[str | int] = []
        if project_id is not None:
            filters.append("project_id = ?")
            parameters.append(project_id)
        if session_id is not None:
            filters.append("session_id = ?")
            parameters.append(session_id)
        if user_id is not None:
            filters.append("user_id = ?")
            parameters.append(user_id)
        where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
        parameters.append(max(0, limit))
        with self._connect() as connection:
            rows = connection.execute(
                f"""
                SELECT * FROM documents
                {where_clause}
                ORDER BY created_at DESC, id DESC
                LIMIT ?
                """,
                tuple(parameters),
            ).fetchall()
        return [self._row_to_document(row) for row in rows]

    def session_belongs_to_project(self, session_id: str, project_id: str) -> bool:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT 1 FROM creative_sessions WHERE id = ? AND project_id = ?",
                (session_id, project_id),
            ).fetchone()
        return row is not None

    def document_belongs_to_project(self, document_id: str, project_id: str) -> bool:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT 1 FROM documents WHERE id = ? AND project_id = ?",
                (document_id, project_id),
            ).fetchone()
        return row is not None

    def document_belongs_to_session(self, document_id: str, session_id: str) -> bool:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT 1 FROM documents WHERE id = ? AND session_id = ?",
                (document_id, session_id),
            ).fetchone()
        return row is not None

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _fetch_project(self, query: str, parameters: tuple[str, ...]) -> ProjectRecord | None:
        with self._connect() as connection:
            row = connection.execute(query, parameters).fetchone()
        if row is None:
            return None
        return self._row_to_project(row)

    def _fetch_session(self, query: str, parameters: tuple[str, ...]) -> CreativeSessionRecord | None:
        with self._connect() as connection:
            row = connection.execute(query, parameters).fetchone()
        if row is None:
            return None
        return self._row_to_session(row)

    def _fetch_document(self, query: str, parameters: tuple[str, ...]) -> DocumentRecord | None:
        with self._connect() as connection:
            row = connection.execute(query, parameters).fetchone()
        if row is None:
            return None
        return self._row_to_document(row)

    @staticmethod
    def _row_to_project(row: sqlite3.Row) -> ProjectRecord:
        return ProjectRecord(
            id=row["id"],
            workspace_id=row["workspace_id"],
            owner_user_id=row["owner_user_id"],
            title=row["title"],
            source_mode=row["source_mode"],
            status=row["status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            last_active_at=row["last_active_at"],
            metadata_json=row["metadata_json"],
        )

    @staticmethod
    def _row_to_session(row: sqlite3.Row) -> CreativeSessionRecord:
        return CreativeSessionRecord(
            id=row["id"],
            project_id=row["project_id"],
            workspace_id=row["workspace_id"],
            user_id=row["user_id"],
            source_mode=row["source_mode"],
            context_policy=row["context_policy"],
            status=row["status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            last_event_at=row["last_event_at"],
            metadata_json=row["metadata_json"],
        )

    @staticmethod
    def _row_to_document(row: sqlite3.Row) -> DocumentRecord:
        return DocumentRecord(
            id=row["id"],
            project_id=row["project_id"],
            session_id=row["session_id"],
            workspace_id=row["workspace_id"],
            user_id=row["user_id"],
            document_type=row["document_type"],
            source_stage=row["source_stage"],
            direction=row["direction"],
            filename_safe=row["filename_safe"],
            content_type=row["content_type"],
            file_size_bytes=row["file_size_bytes"],
            character_count=row["character_count"],
            export_format=row["export_format"],
            status=row["status"],
            created_at=row["created_at"],
            metadata_json=row["metadata_json"],
        )
