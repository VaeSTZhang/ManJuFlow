from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
import sqlite3


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


@dataclass(frozen=True)
class AuthUserRecord:
    id: str
    username: str
    display_name: str
    password_hash: str
    role: str
    workspace_id: str
    default_project_id: str | None
    is_active: bool
    created_at: str
    updated_at: str
    last_login_at: str | None
    password_updated_at: str | None


class SQLiteAuthRepository:
    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)

    def init_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    display_name TEXT,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    workspace_id TEXT NOT NULL,
                    default_project_id TEXT,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_login_at TEXT,
                    password_updated_at TEXT
                )
                """
            )

    def create_user(self, record: AuthUserRecord) -> AuthUserRecord:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO users (
                    id,
                    username,
                    display_name,
                    password_hash,
                    role,
                    workspace_id,
                    default_project_id,
                    is_active,
                    created_at,
                    updated_at,
                    last_login_at,
                    password_updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.id,
                    record.username,
                    record.display_name,
                    record.password_hash,
                    record.role,
                    record.workspace_id,
                    record.default_project_id,
                    int(record.is_active),
                    record.created_at,
                    record.updated_at,
                    record.last_login_at,
                    record.password_updated_at,
                ),
            )
        return record

    def get_user_by_username(self, username: str) -> AuthUserRecord | None:
        normalized_username = username.strip()
        if not normalized_username:
            return None

        return self._fetch_one(
            "SELECT * FROM users WHERE username = ?",
            (normalized_username,),
        )

    def get_user_by_id(self, user_id: str) -> AuthUserRecord | None:
        normalized_user_id = user_id.strip()
        if not normalized_user_id:
            return None

        return self._fetch_one(
            "SELECT * FROM users WHERE id = ?",
            (normalized_user_id,),
        )

    def list_safe_users(self) -> list[dict[str, str | bool | None]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    username,
                    display_name,
                    role,
                    workspace_id,
                    default_project_id,
                    is_active,
                    created_at,
                    updated_at,
                    last_login_at,
                    password_updated_at
                FROM users
                ORDER BY username ASC
                """
            ).fetchall()

        return [
            {
                "id": row["id"],
                "username": row["username"],
                "display_name": row["display_name"],
                "role": row["role"],
                "workspace_id": row["workspace_id"],
                "default_project_id": row["default_project_id"],
                "is_active": bool(row["is_active"]),
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "last_login_at": row["last_login_at"],
                "password_updated_at": row["password_updated_at"],
            }
            for row in rows
        ]

    def update_last_login(self, user_id: str, logged_in_at: str | None = None) -> None:
        timestamp = logged_in_at or _utc_now_iso()
        with self._connect() as connection:
            connection.execute(
                "UPDATE users SET last_login_at = ?, updated_at = ? WHERE id = ?",
                (timestamp, timestamp, user_id),
            )

    def deactivate_user(self, user_id: str) -> None:
        updated_at = _utc_now_iso()
        with self._connect() as connection:
            connection.execute(
                "UPDATE users SET is_active = 0, updated_at = ? WHERE id = ?",
                (updated_at, user_id),
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _fetch_one(self, query: str, parameters: tuple[str, ...]) -> AuthUserRecord | None:
        with self._connect() as connection:
            row = connection.execute(query, parameters).fetchone()

        if row is None:
            return None

        return self._row_to_record(row)

    @staticmethod
    def _row_to_record(row: sqlite3.Row) -> AuthUserRecord:
        return AuthUserRecord(
            id=row["id"],
            username=row["username"],
            display_name=row["display_name"] or "",
            password_hash=row["password_hash"],
            role=row["role"],
            workspace_id=row["workspace_id"],
            default_project_id=row["default_project_id"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            last_login_at=row["last_login_at"],
            password_updated_at=row["password_updated_at"],
        )
