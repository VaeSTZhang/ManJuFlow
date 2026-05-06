from pathlib import Path
import sys


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.repositories.auth_repository import AuthUserRecord, SQLiteAuthRepository  # noqa: E402
from app.services.auth_seed import (  # noqa: E402
    SAFE_CREATOR_TEST_PASSWORD,
    build_safe_creator_seed_user,
    seed_safe_internal_users,
)
from app.services.password_hashing import verify_password  # noqa: E402


def test_build_safe_creator_seed_user_returns_auth_record() -> None:
    seed_user = build_safe_creator_seed_user()

    assert isinstance(seed_user, AuthUserRecord)
    assert seed_user.username == "safe_creator"
    assert seed_user.role == "creator"
    assert seed_user.is_active is True


def test_seed_user_password_hash_is_not_plaintext() -> None:
    seed_user = build_safe_creator_seed_user()

    assert seed_user.password_hash != SAFE_CREATOR_TEST_PASSWORD
    assert SAFE_CREATOR_TEST_PASSWORD not in seed_user.password_hash


def test_seed_user_password_hash_can_be_verified() -> None:
    seed_user = build_safe_creator_seed_user()

    assert verify_password(SAFE_CREATOR_TEST_PASSWORD, seed_user.password_hash) is True


def test_seed_safe_internal_users_writes_to_tmp_path_repository(tmp_path: Path) -> None:
    repository = SQLiteAuthRepository(tmp_path / "auth_seed_test.sqlite")

    seeded_users = seed_safe_internal_users(repository)
    fetched_user = repository.get_user_by_username("safe_creator")

    assert len(seeded_users) == 1
    assert fetched_user is not None
    assert fetched_user.username == "safe_creator"
    assert verify_password(SAFE_CREATOR_TEST_PASSWORD, fetched_user.password_hash) is True


def test_repeated_seed_does_not_create_duplicate_user(tmp_path: Path) -> None:
    repository = SQLiteAuthRepository(tmp_path / "auth_seed_test.sqlite")

    first_seed = seed_safe_internal_users(repository)
    second_seed = seed_safe_internal_users(repository)
    safe_users = repository.list_safe_users()

    assert len(first_seed) == 1
    assert len(second_seed) == 1
    assert len(safe_users) == 1
    assert safe_users[0]["username"] == "safe_creator"


def test_seed_safe_users_list_does_not_include_password_hash(tmp_path: Path) -> None:
    repository = SQLiteAuthRepository(tmp_path / "auth_seed_test.sqlite")

    seed_safe_internal_users(repository)
    safe_users = repository.list_safe_users()

    assert "password_hash" not in safe_users[0]
    assert SAFE_CREATOR_TEST_PASSWORD not in str(safe_users)


def test_seed_does_not_create_database_file_in_repository(tmp_path: Path) -> None:
    repository = SQLiteAuthRepository(tmp_path / "auth_seed_test.sqlite3")

    seed_safe_internal_users(repository)

    assert (tmp_path / "auth_seed_test.sqlite3").exists()
    assert not Path("auth_seed_test.sqlite3").exists()
