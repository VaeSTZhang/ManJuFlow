from pathlib import Path
import sys

import pytest


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.services.password_hashing import hash_password, verify_password  # noqa: E402


SAFE_FAKE_PASSWORD = "SafePass123"


def test_hash_password_returns_string() -> None:
    password_hash = hash_password(SAFE_FAKE_PASSWORD)

    assert isinstance(password_hash, str)
    assert password_hash.startswith("pbkdf2_sha256$")


def test_same_password_hashes_are_different() -> None:
    first_hash = hash_password(SAFE_FAKE_PASSWORD)
    second_hash = hash_password(SAFE_FAKE_PASSWORD)

    assert first_hash != second_hash


def test_verify_password_returns_true_for_correct_password() -> None:
    password_hash = hash_password(SAFE_FAKE_PASSWORD)

    assert verify_password(SAFE_FAKE_PASSWORD, password_hash) is True


def test_verify_password_returns_false_for_wrong_password() -> None:
    password_hash = hash_password(SAFE_FAKE_PASSWORD)

    assert verify_password("WrongPass123", password_hash) is False


def test_verify_password_returns_false_for_malformed_hash() -> None:
    assert verify_password(SAFE_FAKE_PASSWORD, "not-a-valid-hash") is False
    assert verify_password(SAFE_FAKE_PASSWORD, "pbkdf2_sha256$bad$salt$hash") is False


def test_hash_password_rejects_empty_password() -> None:
    with pytest.raises(ValueError):
        hash_password("")

    with pytest.raises(ValueError):
        hash_password("   ")


def test_hash_does_not_contain_plaintext_password() -> None:
    password_hash = hash_password(SAFE_FAKE_PASSWORD)

    assert SAFE_FAKE_PASSWORD not in password_hash
