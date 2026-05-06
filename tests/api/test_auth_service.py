from pathlib import Path
import sys

import pytest


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.repositories.auth_repository import AuthUserRecord, SQLiteAuthRepository
from app.schemas.auth import AuthLoginOutput
from app.services.auth_service import (
    AUTH_INVALID_CREDENTIALS_MESSAGE,
    AuthError,
    authenticate_internal_user,
    configure_auth_repository_for_testing,
    get_safe_internal_user,
    list_safe_internal_users,
    reset_auth_repository_for_testing,
)
from app.services.password_hashing import hash_password


@pytest.fixture(autouse=True)
def isolated_auth_repository(tmp_path: Path):
    repository = SQLiteAuthRepository(tmp_path / "auth_service_test.sqlite")
    configure_auth_repository_for_testing(repository)
    yield repository
    reset_auth_repository_for_testing()


def test_authenticate_safe_creator_success() -> None:
    output = authenticate_internal_user("safe_creator", "SafePass123")

    assert isinstance(output, AuthLoginOutput)
    assert output.user.username == "safe_creator"
    assert output.user.role == "creator"
    assert output.user.status == "active"
    assert output.session.context_policy == "current_project_only"
    assert output.access_token == "safe_mock_token_user_safe_creator_001"
    assert output.token_type == "bearer"


def test_authenticate_trims_username() -> None:
    output = authenticate_internal_user("  safe_creator  ", "SafePass123")

    assert output.user.username == "safe_creator"


def test_authenticate_output_does_not_include_password_or_hash() -> None:
    output = authenticate_internal_user("safe_creator", "SafePass123")
    dumped_text = str(output.model_dump())

    assert "SafePass123" not in dumped_text
    assert "password" not in dumped_text
    assert "password_hash" not in dumped_text


def test_authenticate_updates_last_login(isolated_auth_repository: SQLiteAuthRepository) -> None:
    assert isolated_auth_repository.get_user_by_username("safe_creator") is not None

    authenticate_internal_user("safe_creator", "SafePass123")
    stored_user = isolated_auth_repository.get_user_by_username("safe_creator")

    assert stored_user is not None
    assert stored_user.last_login_at is not None


def test_unknown_username_fails_with_generic_message() -> None:
    with pytest.raises(AuthError) as exc_info:
        authenticate_internal_user("missing_user", "SafePass123")

    assert str(exc_info.value) == AUTH_INVALID_CREDENTIALS_MESSAGE


def test_wrong_password_fails_with_generic_message() -> None:
    with pytest.raises(AuthError) as exc_info:
        authenticate_internal_user("safe_creator", "WrongPass123")

    assert str(exc_info.value) == AUTH_INVALID_CREDENTIALS_MESSAGE


def test_empty_username_fails() -> None:
    with pytest.raises(AuthError) as exc_info:
        authenticate_internal_user(" ", "SafePass123")

    assert str(exc_info.value) == AUTH_INVALID_CREDENTIALS_MESSAGE


def test_empty_password_fails() -> None:
    with pytest.raises(AuthError) as exc_info:
        authenticate_internal_user("safe_creator", " ")

    assert str(exc_info.value) == AUTH_INVALID_CREDENTIALS_MESSAGE


def test_policy_invalid_password_fails_with_generic_message() -> None:
    with pytest.raises(AuthError) as exc_info:
        authenticate_internal_user("safe_creator", "short")

    assert str(exc_info.value) == AUTH_INVALID_CREDENTIALS_MESSAGE
    assert "short" not in str(exc_info.value)


def test_inactive_user_fails_with_generic_message(isolated_auth_repository: SQLiteAuthRepository) -> None:
    inactive_user = AuthUserRecord(
        id="user_safe_inactive_001",
        username="safe_inactive",
        display_name="安全测试停用账号",
        password_hash=hash_password("SafePass123"),
        role="creator",
        workspace_id="workspace_dramora_internal",
        default_project_id="project_creation_default",
        is_active=False,
        created_at="2026-05-06T00:00:00+00:00",
        updated_at="2026-05-06T00:00:00+00:00",
        last_login_at=None,
        password_updated_at="2026-05-06T00:00:00+00:00",
    )
    isolated_auth_repository.create_user(inactive_user)

    with pytest.raises(AuthError) as exc_info:
        authenticate_internal_user("safe_inactive", "SafePass123")

    assert str(exc_info.value) == AUTH_INVALID_CREDENTIALS_MESSAGE


def test_failure_message_does_not_distinguish_unknown_user_and_wrong_password() -> None:
    errors = []

    for username, password in [
        ("missing_user", "SafePass123"),
        ("safe_creator", "WrongPass123"),
    ]:
        with pytest.raises(AuthError) as exc_info:
            authenticate_internal_user(username, password)
        errors.append(str(exc_info.value))

    assert errors == [AUTH_INVALID_CREDENTIALS_MESSAGE, AUTH_INVALID_CREDENTIALS_MESSAGE]


def test_get_safe_internal_user_does_not_return_password() -> None:
    user = get_safe_internal_user("safe_creator")

    assert user is not None
    assert user.username == "safe_creator"
    dumped_text = str(user.model_dump())
    assert "password" not in dumped_text
    assert "SafePass123" not in dumped_text
    assert "password_hash" not in dumped_text


def test_get_safe_internal_user_returns_none_for_missing_user() -> None:
    assert get_safe_internal_user("missing_user") is None


def test_list_safe_internal_users_does_not_return_password() -> None:
    users = list_safe_internal_users()

    assert len(users) >= 1
    dumped_text = str([user.model_dump() for user in users])
    assert "password" not in dumped_text
    assert "SafePass123" not in dumped_text
    assert "password_hash" not in dumped_text
