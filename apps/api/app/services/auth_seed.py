from datetime import UTC, datetime

from app.repositories.auth_repository import AuthUserRecord, SQLiteAuthRepository
from app.services.password_hashing import hash_password


# Development/test-only safe fictional password. Replace before any internal deployment.
SAFE_CREATOR_TEST_PASSWORD = "SafePass123"
SAFE_CREATOR_USERNAME = "safe_creator"
SAFE_CREATOR_USER_ID = "user_safe_creator_001"


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def build_safe_creator_seed_user() -> AuthUserRecord:
    created_at = _utc_now_iso()
    return AuthUserRecord(
        id=SAFE_CREATOR_USER_ID,
        username=SAFE_CREATOR_USERNAME,
        display_name="安全测试创作者",
        password_hash=hash_password(SAFE_CREATOR_TEST_PASSWORD),
        role="creator",
        workspace_id="workspace_dramora_internal",
        default_project_id="project_creation_default",
        is_active=True,
        created_at=created_at,
        updated_at=created_at,
        last_login_at=None,
        password_updated_at=created_at,
    )


def seed_safe_internal_users(repository: SQLiteAuthRepository) -> list[AuthUserRecord]:
    repository.init_schema()
    existing_user = repository.get_user_by_username(SAFE_CREATOR_USERNAME)
    if existing_user is not None:
        return [existing_user]

    seed_user = build_safe_creator_seed_user()
    repository.create_user(seed_user)
    return [seed_user]
