from pathlib import Path
import sys

import pytest


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.services.auth_password_policy import (
    PASSWORD_POLICY_MIN_LENGTH,
    check_internal_password_policy,
    validate_internal_password_policy,
)


def test_safe_password_passes_policy() -> None:
    validate_internal_password_policy("SafePass123")


def test_password_without_uppercase_fails() -> None:
    with pytest.raises(ValueError, match="has_uppercase"):
        validate_internal_password_policy("safepass123")


def test_password_without_lowercase_fails() -> None:
    with pytest.raises(ValueError, match="has_lowercase"):
        validate_internal_password_policy("SAFEPASS123")


def test_password_without_digit_fails() -> None:
    with pytest.raises(ValueError, match="has_digit"):
        validate_internal_password_policy("SafePassword")


def test_short_password_fails() -> None:
    with pytest.raises(ValueError, match="min_length"):
        validate_internal_password_policy("Safe12")


def test_empty_password_fails() -> None:
    with pytest.raises(ValueError):
        validate_internal_password_policy("")


def test_blank_password_fails() -> None:
    with pytest.raises(ValueError):
        validate_internal_password_policy("   ")


def test_special_character_is_not_required() -> None:
    validate_internal_password_policy("SafePass123")


def test_check_internal_password_policy_returns_rule_flags() -> None:
    result = check_internal_password_policy("SafePass")

    assert result == {
        "min_length": True,
        "has_uppercase": True,
        "has_lowercase": True,
        "has_digit": False,
        "valid": False,
    }


def test_error_message_does_not_include_original_password() -> None:
    password = "Badpass"

    with pytest.raises(ValueError) as exc_info:
        validate_internal_password_policy(password)

    message = str(exc_info.value)
    assert password not in message
    assert "Badpass" not in message
    assert "SafePass" not in message


def test_helper_does_not_hash_password_or_return_token() -> None:
    result = check_internal_password_policy("SafePass123")

    assert "password_hash" not in result
    assert "token" not in result
    assert "access_token" not in result
    assert PASSWORD_POLICY_MIN_LENGTH == 8
