from pathlib import Path
import sqlite3
import sys

import pytest


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.repositories.auth_repository import AuthUserRecord, SQLiteAuthRepository  # noqa: E402


def build_safe_user_record(**overrides) -> AuthUserRecord:
    data = {
        "id": "user_safe_creator_001",
        "username": "safe_creator",
        "display_name": "安全测试创作者",
        "password_hash": "test_hash_not_real",
        "role": "creator",
        "workspace_id": "workspace_dramora_internal",
        "default_project_id": "project_creation_default",
        "is_active": True,
        "created_at": "2026-05-06T00:00:00+00:00",
        "updated_at": "2026-05-06T00:00:00+00:00",
        "last_login_at": None,
        "password_updated_at": None,
    }
    data.update(overrides)
    return AuthUserRecord(**data)


@pytest.fixture
def repository(tmp_path: Path) -> SQLiteAuthRepository:
    repo = SQLiteAuthRepository(tmp_path / "auth_test.sqlite")
    repo.init_schema()
    return repo


def test_init_schema_creates_users_table(tmp_path: Path) -> None:
    repo = SQLiteAuthRepository(tmp_path / "auth_test.sqlite")

    repo.init_schema()
    repo.init_schema()

    with sqlite3.connect(tmp_path / "auth_test.sqlite") as connection:
        table = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'users'"
        ).fetchone()

    assert table is not None


def test_create_user_and_get_user_by_username(repository: SQLiteAuthRepository) -> None:
    record = build_safe_user_record()

    repository.create_user(record)
    fetched = repository.get_user_by_username("safe_creator")

    assert fetched == record
    assert fetched is not None
    assert fetched.password_hash == "test_hash_not_real"


def test_create_user_and_get_user_by_id(repository: SQLiteAuthRepository) -> None:
    record = build_safe_user_record()

    repository.create_user(record)
    fetched = repository.get_user_by_id("user_safe_creator_001")

    assert fetched == record


def test_get_user_by_username_returns_none_for_missing_user(repository: SQLiteAuthRepository) -> None:
    assert repository.get_user_by_username("missing_user") is None
    assert repository.get_user_by_username(" ") is None


def test_list_safe_users_does_not_include_password_hash(repository: SQLiteAuthRepository) -> None:
    repository.create_user(build_safe_user_record())

    users = repository.list_safe_users()

    assert users
    assert users[0]["username"] == "safe_creator"
    assert "password_hash" not in users[0]
    assert "test_hash_not_real" not in str(users)


def test_deactivate_user_sets_is_active_false(repository: SQLiteAuthRepository) -> None:
    repository.create_user(build_safe_user_record())

    repository.deactivate_user("user_safe_creator_001")
    fetched = repository.get_user_by_id("user_safe_creator_001")

    assert fetched is not None
    assert fetched.is_active is False
    assert fetched.updated_at != "2026-05-06T00:00:00+00:00"


def test_update_last_login_writes_last_login_at(repository: SQLiteAuthRepository) -> None:
    repository.create_user(build_safe_user_record())

    repository.update_last_login("user_safe_creator_001", "2026-05-06T01:00:00+00:00")
    fetched = repository.get_user_by_id("user_safe_creator_001")

    assert fetched is not None
    assert fetched.last_login_at == "2026-05-06T01:00:00+00:00"
    assert fetched.updated_at == "2026-05-06T01:00:00+00:00"


def test_duplicate_username_fails(repository: SQLiteAuthRepository) -> None:
    repository.create_user(build_safe_user_record(id="user_safe_creator_001"))

    with pytest.raises(sqlite3.IntegrityError):
        repository.create_user(build_safe_user_record(id="user_safe_creator_002"))


def test_repository_tests_use_tmp_path(tmp_path: Path) -> None:
    repo = SQLiteAuthRepository(tmp_path / "auth_test.sqlite3")
    repo.init_schema()
    repo.create_user(build_safe_user_record())

    assert (tmp_path / "auth_test.sqlite3").exists()
    assert not Path("auth_test.sqlite3").exists()
