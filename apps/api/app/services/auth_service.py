from pathlib import Path
import os

from app.repositories.auth_repository import AuthUserRecord, SQLiteAuthRepository
from app.schemas.auth import AuthLoginOutput, AuthSession, InternalUser
from app.services.auth_password_policy import validate_internal_password_policy
from app.services.auth_seed import seed_safe_internal_users
from app.services.password_hashing import verify_password


AUTH_INVALID_CREDENTIALS_MESSAGE = "账号或密码不正确。"
AUTH_DB_PATH_ENV_VAR = "DRAMORA_AUTH_DB_PATH"
DEFAULT_AUTH_DB_PATH = Path(".local") / "dramora_auth.sqlite3"

_auth_repository_override: SQLiteAuthRepository | None = None
_default_auth_repository: SQLiteAuthRepository | None = None


class AuthError(ValueError):
    pass


def get_default_auth_database_path() -> Path:
    configured_path = os.getenv(AUTH_DB_PATH_ENV_VAR)
    if configured_path:
        return Path(configured_path)
    return DEFAULT_AUTH_DB_PATH


def get_auth_repository() -> SQLiteAuthRepository:
    if _auth_repository_override is not None:
        return _auth_repository_override

    global _default_auth_repository
    if _default_auth_repository is None:
        database_path = get_default_auth_database_path()
        database_path.parent.mkdir(parents=True, exist_ok=True)
        _default_auth_repository = SQLiteAuthRepository(database_path)
        seed_safe_internal_users(_default_auth_repository)

    return _default_auth_repository


def configure_auth_repository_for_testing(repository: SQLiteAuthRepository) -> None:
    global _auth_repository_override
    repository.init_schema()
    seed_safe_internal_users(repository)
    _auth_repository_override = repository


def reset_auth_repository_for_testing() -> None:
    global _auth_repository_override
    _auth_repository_override = None


def get_safe_internal_user(username: str) -> InternalUser | None:
    user_record = get_auth_repository().get_user_by_username(username)
    if user_record is None:
        return None
    return _safe_user_from_record(user_record)


def list_safe_internal_users() -> list[InternalUser]:
    return [
        InternalUser(
            user_id=str(record["id"]),
            username=str(record["username"]),
            display_name=str(record["display_name"]) if record["display_name"] else None,
            role=_safe_role(str(record["role"])),
            status="active" if record["is_active"] else "disabled",
            workspace_id=str(record["workspace_id"]),
        )
        for record in get_auth_repository().list_safe_users()
    ]


def authenticate_internal_user(username: str, password: str) -> AuthLoginOutput:
    normalized_username = username.strip()

    if not normalized_username or not password.strip():
        raise AuthError(AUTH_INVALID_CREDENTIALS_MESSAGE)

    try:
        validate_internal_password_policy(password)
    except ValueError as exc:
        raise AuthError(AUTH_INVALID_CREDENTIALS_MESSAGE) from exc

    repository = get_auth_repository()
    user_record = repository.get_user_by_username(normalized_username)
    if user_record is None:
        raise AuthError(AUTH_INVALID_CREDENTIALS_MESSAGE)

    if not user_record.is_active:
        raise AuthError(AUTH_INVALID_CREDENTIALS_MESSAGE)

    if not verify_password(password, user_record.password_hash):
        raise AuthError(AUTH_INVALID_CREDENTIALS_MESSAGE)

    repository.update_last_login(user_record.id)
    user = _safe_user_from_record(user_record)
    session = AuthSession(
        session_id=f"session_mock_{user.user_id}",
        user_id=user.user_id,
        workspace_id=user.workspace_id,
        role=user.role,
        status=user.status,
        context_policy="current_project_only",
    )

    return AuthLoginOutput(
        user=user,
        session=session,
        access_token=f"safe_mock_token_{user.user_id}",
        token_type="bearer",
    )


def _safe_user_from_record(record: AuthUserRecord) -> InternalUser:
    return InternalUser(
        user_id=record.id,
        username=record.username,
        display_name=record.display_name or None,
        role=_safe_role(record.role),
        status="active" if record.is_active else "disabled",
        workspace_id=record.workspace_id,
    )


def _safe_role(role: str):
    if role in {"admin", "creator", "reviewer", "viewer"}:
        return role
    return "creator"
