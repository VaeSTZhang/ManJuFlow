from pathlib import Path
import sys

import pytest
from pydantic import ValidationError


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.schemas.auth import AuthLoginInput, AuthLoginOutput, AuthSession, InternalUser


def build_safe_user(**overrides) -> InternalUser:
    data = {
        "user_id": "user_safe_001",
        "username": "internal_creator",
        "display_name": "安全测试用户",
        "workspace_id": "workspace_dramora_internal",
    }
    data.update(overrides)
    return InternalUser(**data)


def build_safe_session(**overrides) -> AuthSession:
    data = {
        "session_id": "session_safe_001",
        "user_id": "user_safe_001",
        "workspace_id": "workspace_dramora_internal",
        "role": "creator",
        "status": "active",
    }
    data.update(overrides)
    return AuthSession(**data)


def test_internal_user_supports_chinese_username() -> None:
    user = build_safe_user(username="张三")

    assert user.username == "张三"


def test_internal_user_supports_english_username() -> None:
    user = build_safe_user(username="creator.alice")

    assert user.username == "creator.alice"


def test_internal_user_defaults_role_and_status() -> None:
    user = InternalUser(user_id="user_safe_001", username="safe_creator")

    assert user.role == "creator"
    assert user.status == "active"


def test_internal_user_rejects_empty_user_id() -> None:
    with pytest.raises(ValidationError):
        InternalUser(user_id=" ", username="safe_creator")


def test_internal_user_rejects_empty_username() -> None:
    with pytest.raises(ValidationError):
        InternalUser(user_id="user_safe_001", username=" ")


def test_internal_user_metadata_defaults_do_not_pollute_instances() -> None:
    first_user = build_safe_user(user_id="user_safe_001")
    second_user = build_safe_user(user_id="user_safe_002")

    first_user.metadata["department"] = "content"

    assert second_user.metadata == {}


def test_auth_login_input_accepts_safe_fake_password() -> None:
    login_input = AuthLoginInput(username="safe_creator", password="SafePass123")

    assert login_input.username == "safe_creator"
    assert login_input.password == "SafePass123"


def test_auth_login_input_rejects_empty_username() -> None:
    with pytest.raises(ValidationError):
        AuthLoginInput(username=" ", password="SafePass123")


def test_auth_login_input_rejects_empty_password() -> None:
    with pytest.raises(ValidationError):
        AuthLoginInput(username="safe_creator", password=" ")


def test_auth_session_defaults_context_policy() -> None:
    session = build_safe_session()

    assert session.context_policy == "current_project_only"


def test_auth_login_output_contains_user_session_and_safe_token() -> None:
    output = AuthLoginOutput(
        user=build_safe_user(),
        session=build_safe_session(),
        access_token="safe_test_token",
    )

    assert output.user.user_id == "user_safe_001"
    assert output.session.session_id == "session_safe_001"
    assert output.access_token == "safe_test_token"
    assert output.token_type == "bearer"


def test_auth_login_output_model_dump_does_not_include_password() -> None:
    output = AuthLoginOutput(
        user=build_safe_user(),
        session=build_safe_session(),
        access_token="safe_test_token",
    )
    dumped = output.model_dump()
    dumped_text = str(dumped)

    assert "password" not in dumped_text
    assert "password_hash" not in dumped_text


def test_auth_schema_uses_only_safe_fake_values() -> None:
    output = AuthLoginOutput(
        user=build_safe_user(username="safe_creator"),
        session=build_safe_session(),
        access_token="safe_test_token",
    )
    dumped_text = str(output.model_dump())

    assert "SafePass123" not in dumped_text
    assert "safe_test_token" in dumped_text
    assert "API_KEY" not in dumped_text
    assert ".env" not in dumped_text
