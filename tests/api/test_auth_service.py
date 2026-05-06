from pathlib import Path
import sys

import pytest


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.schemas.auth import AuthLoginOutput
from app.services.auth_service import (
    AUTH_INVALID_CREDENTIALS_MESSAGE,
    AuthError,
    authenticate_internal_user,
    get_safe_internal_user,
    list_safe_internal_users,
)


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


def test_get_safe_internal_user_returns_none_for_missing_user() -> None:
    assert get_safe_internal_user("missing_user") is None


def test_list_safe_internal_users_does_not_return_password() -> None:
    users = list_safe_internal_users()

    assert len(users) >= 1
    dumped_text = str([user.model_dump() for user in users])
    assert "password" not in dumped_text
    assert "SafePass123" not in dumped_text
