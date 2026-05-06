from copy import deepcopy
from typing import Any

from app.schemas.auth import AuthLoginOutput, AuthSession, InternalUser
from app.services.auth_password_policy import validate_internal_password_policy


AUTH_INVALID_CREDENTIALS_MESSAGE = "账号或密码不正确。"

SAFE_INTERNAL_AUTH_USERS: dict[str, dict[str, Any]] = {
    "safe_creator": {
        "user_id": "user_safe_creator_001",
        "username": "safe_creator",
        "display_name": "安全测试创作者",
        "password": "SafePass123",
        "role": "creator",
        "status": "active",
        "workspace_id": "workspace_dramora_internal",
    }
}


class AuthError(ValueError):
    pass


def _safe_user_from_record(record: dict[str, Any]) -> InternalUser:
    safe_record = {key: value for key, value in record.items() if key != "password"}
    return InternalUser(**safe_record)


def get_safe_internal_user(username: str) -> InternalUser | None:
    normalized_username = username.strip()
    if not normalized_username:
        return None

    record = SAFE_INTERNAL_AUTH_USERS.get(normalized_username)
    if record is None:
        return None

    return _safe_user_from_record(deepcopy(record))


def list_safe_internal_users() -> list[InternalUser]:
    return [_safe_user_from_record(deepcopy(record)) for record in SAFE_INTERNAL_AUTH_USERS.values()]


def authenticate_internal_user(username: str, password: str) -> AuthLoginOutput:
    normalized_username = username.strip()

    if not normalized_username or not password.strip():
        raise AuthError(AUTH_INVALID_CREDENTIALS_MESSAGE)

    try:
        validate_internal_password_policy(password)
    except ValueError as exc:
        raise AuthError(AUTH_INVALID_CREDENTIALS_MESSAGE) from exc

    record = SAFE_INTERNAL_AUTH_USERS.get(normalized_username)
    if record is None:
        raise AuthError(AUTH_INVALID_CREDENTIALS_MESSAGE)

    if record["password"] != password:
        raise AuthError(AUTH_INVALID_CREDENTIALS_MESSAGE)

    if record["status"] != "active":
        raise AuthError(AUTH_INVALID_CREDENTIALS_MESSAGE)

    user = _safe_user_from_record(deepcopy(record))
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
