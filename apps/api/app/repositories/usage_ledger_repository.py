from dataclasses import dataclass
from pathlib import Path
import sqlite3


@dataclass(frozen=True)
class UsageLedgerRecord:
    id: str
    request_id: str | None
    user_id: str | None
    username: str | None
    workspace_id: str | None
    project_id: str | None
    session_id: str | None
    context_policy: str
    operation: str
    purpose: str | None
    provider: str | None
    model: str | None
    generation_mode: str | None
    status: str
    source_mode: str | None
    document_operation: str | None
    input_character_count: int | None
    output_character_count: int | None
    prompt_token_count: int | None
    completion_token_count: int | None
    total_token_count: int | None
    estimated_cost_cny: float | None
    latency_ms: int | None
    error_code: str | None
    error_message_safe: str | None
    created_at: str
    metadata_json: str | None


class SQLiteUsageLedgerRepository:
    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)

    def init_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS usage_ledger (
                    id TEXT PRIMARY KEY,
                    request_id TEXT,
                    user_id TEXT,
                    username TEXT,
                    workspace_id TEXT,
                    project_id TEXT,
                    session_id TEXT,
                    context_policy TEXT NOT NULL DEFAULT 'current_project_only',
                    operation TEXT NOT NULL,
                    purpose TEXT,
                    provider TEXT,
                    model TEXT,
                    generation_mode TEXT,
                    status TEXT NOT NULL,
                    source_mode TEXT,
                    document_operation TEXT,
                    input_character_count INTEGER,
                    output_character_count INTEGER,
                    prompt_token_count INTEGER,
                    completion_token_count INTEGER,
                    total_token_count INTEGER,
                    estimated_cost_cny REAL,
                    latency_ms INTEGER,
                    error_code TEXT,
                    error_message_safe TEXT,
                    created_at TEXT NOT NULL,
                    metadata_json TEXT
                )
                """
            )
            for index_name, column_name in [
                ("idx_usage_ledger_request_id", "request_id"),
                ("idx_usage_ledger_user_id", "user_id"),
                ("idx_usage_ledger_workspace_id", "workspace_id"),
                ("idx_usage_ledger_project_id", "project_id"),
                ("idx_usage_ledger_provider", "provider"),
                ("idx_usage_ledger_operation", "operation"),
                ("idx_usage_ledger_created_at", "created_at"),
            ]:
                connection.execute(
                    f"CREATE INDEX IF NOT EXISTS {index_name} ON usage_ledger ({column_name})"
                )

    def create_entry(self, record: UsageLedgerRecord) -> UsageLedgerRecord:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO usage_ledger (
                    id,
                    request_id,
                    user_id,
                    username,
                    workspace_id,
                    project_id,
                    session_id,
                    context_policy,
                    operation,
                    purpose,
                    provider,
                    model,
                    generation_mode,
                    status,
                    source_mode,
                    document_operation,
                    input_character_count,
                    output_character_count,
                    prompt_token_count,
                    completion_token_count,
                    total_token_count,
                    estimated_cost_cny,
                    latency_ms,
                    error_code,
                    error_message_safe,
                    created_at,
                    metadata_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.id,
                    record.request_id,
                    record.user_id,
                    record.username,
                    record.workspace_id,
                    record.project_id,
                    record.session_id,
                    record.context_policy,
                    record.operation,
                    record.purpose,
                    record.provider,
                    record.model,
                    record.generation_mode,
                    record.status,
                    record.source_mode,
                    record.document_operation,
                    record.input_character_count,
                    record.output_character_count,
                    record.prompt_token_count,
                    record.completion_token_count,
                    record.total_token_count,
                    record.estimated_cost_cny,
                    record.latency_ms,
                    record.error_code,
                    record.error_message_safe,
                    record.created_at,
                    record.metadata_json,
                ),
            )
        return record

    def get_entry_by_request_id(self, request_id: str) -> UsageLedgerRecord | None:
        normalized_request_id = request_id.strip()
        if not normalized_request_id:
            return None

        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM usage_ledger WHERE request_id = ?",
                (normalized_request_id,),
            ).fetchone()

        if row is None:
            return None
        return self._row_to_record(row)

    def list_entries(
        self,
        limit: int = 100,
        user_id: str | None = None,
        workspace_id: str | None = None,
        project_id: str | None = None,
    ) -> list[UsageLedgerRecord]:
        filters: list[str] = []
        parameters: list[str | int] = []

        if user_id is not None:
            filters.append("user_id = ?")
            parameters.append(user_id)
        if workspace_id is not None:
            filters.append("workspace_id = ?")
            parameters.append(workspace_id)
        if project_id is not None:
            filters.append("project_id = ?")
            parameters.append(project_id)

        where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
        query = f"""
            SELECT * FROM usage_ledger
            {where_clause}
            ORDER BY created_at DESC, id DESC
            LIMIT ?
        """
        parameters.append(max(0, limit))

        with self._connect() as connection:
            rows = connection.execute(query, tuple(parameters)).fetchall()

        return [self._row_to_record(row) for row in rows]

    def summarize_by_user(self) -> list[dict[str, str | int | float | None]]:
        return self._fetch_summary(
            """
            SELECT
                user_id,
                COUNT(*) AS entry_count,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) AS success_count,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed_count,
                COALESCE(SUM(estimated_cost_cny), 0) AS estimated_cost_cny_total
            FROM usage_ledger
            GROUP BY user_id
            ORDER BY entry_count DESC, user_id ASC
            """
        )

    def summarize_by_provider(self) -> list[dict[str, str | int | float | None]]:
        return self._fetch_summary(
            """
            SELECT
                provider,
                COUNT(*) AS entry_count,
                COALESCE(SUM(estimated_cost_cny), 0) AS estimated_cost_cny_total
            FROM usage_ledger
            GROUP BY provider
            ORDER BY entry_count DESC, provider ASC
            """
        )

    def summarize_by_operation(self) -> list[dict[str, str | int | float | None]]:
        return self._fetch_summary(
            """
            SELECT
                operation,
                COUNT(*) AS entry_count,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) AS success_count,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed_count
            FROM usage_ledger
            GROUP BY operation
            ORDER BY entry_count DESC, operation ASC
            """
        )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _fetch_summary(self, query: str) -> list[dict[str, str | int | float | None]]:
        with self._connect() as connection:
            rows = connection.execute(query).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def _row_to_record(row: sqlite3.Row) -> UsageLedgerRecord:
        return UsageLedgerRecord(
            id=row["id"],
            request_id=row["request_id"],
            user_id=row["user_id"],
            username=row["username"],
            workspace_id=row["workspace_id"],
            project_id=row["project_id"],
            session_id=row["session_id"],
            context_policy=row["context_policy"],
            operation=row["operation"],
            purpose=row["purpose"],
            provider=row["provider"],
            model=row["model"],
            generation_mode=row["generation_mode"],
            status=row["status"],
            source_mode=row["source_mode"],
            document_operation=row["document_operation"],
            input_character_count=row["input_character_count"],
            output_character_count=row["output_character_count"],
            prompt_token_count=row["prompt_token_count"],
            completion_token_count=row["completion_token_count"],
            total_token_count=row["total_token_count"],
            estimated_cost_cny=row["estimated_cost_cny"],
            latency_ms=row["latency_ms"],
            error_code=row["error_code"],
            error_message_safe=row["error_message_safe"],
            created_at=row["created_at"],
            metadata_json=row["metadata_json"],
        )
