from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.repositories.auth_repository import SQLiteAuthRepository  # noqa: E402
from app.services.auth_service import (  # noqa: E402
    AUTH_INVALID_CREDENTIALS_MESSAGE,
    configure_auth_repository_for_testing,
    reset_auth_repository_for_testing,
)
from app.main import app  # noqa: E402


client = TestClient(app)


@pytest.fixture(autouse=True)
def isolated_auth_repository(tmp_path: Path):
    repository = SQLiteAuthRepository(tmp_path / "auth_endpoint_test.sqlite")
    configure_auth_repository_for_testing(repository)
    yield repository
    reset_auth_repository_for_testing()


def test_auth_login_returns_safe_creator_session() -> None:
    response = client.post(
        "/api/auth/login",
        json={"username": "safe_creator", "password": "SafePass123"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["user"]["username"] == "safe_creator"
    assert body["user"]["role"] == "creator"
    assert body["user"]["status"] == "active"
    assert body["session"]["context_policy"] == "current_project_only"
    assert body["token_type"] == "bearer"
    assert body["access_token"] == "safe_mock_token_user_safe_creator_001"


def test_auth_login_response_does_not_expose_password_or_hash() -> None:
    response = client.post(
        "/api/auth/login",
        json={"username": "safe_creator", "password": "SafePass123"},
    )

    assert response.status_code == 200
    response_text = response.text
    assert "SafePass123" not in response_text
    assert "password_hash" not in response_text
    assert '"password"' not in response_text


def test_auth_login_wrong_username_returns_401() -> None:
    response = client.post(
        "/api/auth/login",
        json={"username": "missing_user", "password": "SafePass123"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == AUTH_INVALID_CREDENTIALS_MESSAGE
    assert "SafePass123" not in response.text
    assert "password_hash" not in response.text


def test_auth_login_wrong_password_returns_401() -> None:
    response = client.post(
        "/api/auth/login",
        json={"username": "safe_creator", "password": "WrongPass123"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == AUTH_INVALID_CREDENTIALS_MESSAGE
    assert "WrongPass123" not in response.text
    assert "password_hash" not in response.text


def test_auth_login_failure_detail_does_not_distinguish_failure_reason() -> None:
    wrong_username_response = client.post(
        "/api/auth/login",
        json={"username": "missing_user", "password": "SafePass123"},
    )
    wrong_password_response = client.post(
        "/api/auth/login",
        json={"username": "safe_creator", "password": "WrongPass123"},
    )

    assert wrong_username_response.status_code == 401
    assert wrong_password_response.status_code == 401
    assert wrong_username_response.json()["detail"] == wrong_password_response.json()["detail"]


def test_auth_login_empty_password_returns_validation_or_auth_error() -> None:
    response = client.post(
        "/api/auth/login",
        json={"username": "safe_creator", "password": ""},
    )

    assert response.status_code in {401, 422}
    assert "SafePass123" not in response.text
    assert "password_hash" not in response.text


def test_auth_safe_users_returns_sanitized_internal_users() -> None:
    response = client.get("/api/auth/safe-users")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert any(user["username"] == "safe_creator" for user in body)
    response_text = response.text
    assert "SafePass123" not in response_text
    assert "password_hash" not in response_text
    assert '"password"' not in response_text


def test_auth_endpoints_are_in_openapi_schema() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/api/auth/login" in paths
    assert "/api/auth/safe-users" in paths
