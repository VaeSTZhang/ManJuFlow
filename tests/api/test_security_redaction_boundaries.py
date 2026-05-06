from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.config import get_settings  # noqa: E402
from app.main import app  # noqa: E402
from app.repositories.auth_repository import SQLiteAuthRepository  # noqa: E402
from app.repositories.ownership_repository import (  # noqa: E402
    CreativeSessionRecord,
    DocumentRecord,
    ProjectRecord,
    SQLiteOwnershipRepository,
)
from app.repositories.usage_ledger_repository import SQLiteUsageLedgerRepository  # noqa: E402
from app.schemas.context import ContextOptions  # noqa: E402
from app.schemas.script import EpisodeScript  # noqa: E402
from app.schemas.script_generation import ShortDramaScriptOutput  # noqa: E402
from app.schemas.usage_ledger import UsageLedgerCreate  # noqa: E402
from app.services.auth_service import (  # noqa: E402
    AUTH_INVALID_CREDENTIALS_MESSAGE,
    configure_auth_repository_for_testing,
    reset_auth_repository_for_testing,
)
from app.services.ownership_service import (  # noqa: E402
    OwnershipError,
    configure_ownership_repository_for_testing,
    get_document_for_context,
    reset_ownership_repository_for_testing,
)
from app.services.usage_ledger_service import (  # noqa: E402
    configure_usage_ledger_repository_for_testing,
    create_usage_ledger_entry,
    reset_usage_ledger_repository_for_testing,
)


SAFE_SOURCE_TEXT = "安全虚构电影剧本片段：完整输入正文不应出现在错误响应。"
SAFE_CONTENT_TEXT = "安全虚构导出正文：完整导出文本不应出现在错误响应。"
SAFE_PROVIDER_RAW_RESPONSE = "provider 原始响应安全占位，不应写入记录。"
SAFE_API_KEY = "not-a-real-api-key"
SAFE_PASSWORD = "WrongPass123"
SAFE_TOKEN = "not-a-real-access-token"
NOW = "2026-05-06T00:00:00+00:00"

FORBIDDEN_RESPONSE_VALUES = [
    "SafePass123",
    SAFE_PASSWORD,
    "password_hash",
    "access_token",
    "session_token",
    ".sqlite",
    ".db",
    "/Users/",
    SAFE_SOURCE_TEXT,
    SAFE_CONTENT_TEXT,
    SAFE_PROVIDER_RAW_RESPONSE,
    SAFE_API_KEY,
    SAFE_TOKEN,
]


@pytest.fixture(autouse=True)
def isolated_security_repositories(tmp_path: Path):
    auth_repository = SQLiteAuthRepository(tmp_path / "security_auth.sqlite")
    usage_repository = SQLiteUsageLedgerRepository(tmp_path / "security_usage.sqlite")
    ownership_repository = SQLiteOwnershipRepository(tmp_path / "security_ownership.sqlite")
    configure_auth_repository_for_testing(auth_repository)
    configure_usage_ledger_repository_for_testing(usage_repository)
    configure_ownership_repository_for_testing(ownership_repository)
    yield {
        "auth": auth_repository,
        "usage": usage_repository,
        "ownership": ownership_repository,
    }
    reset_auth_repository_for_testing()
    reset_usage_ledger_repository_for_testing()
    reset_ownership_repository_for_testing()


def assert_text_is_redacted(text: str) -> None:
    for forbidden in FORBIDDEN_RESPONSE_VALUES:
        assert forbidden not in text


def make_source_request(**overrides) -> dict:
    data = {
        "project_title": "安全虚构短剧",
        "source_mode": "film_script",
        "source_text": SAFE_SOURCE_TEXT,
        "target_episode_count": 3,
        "genre": "悬疑短剧",
        "style": "强钩子、快节奏",
        "language": "zh",
        "context_options": {
            "request_id": "request_security_contract_failed",
            "project_id": "project_security_contract",
            "session_id": "session_security_contract",
        },
    }
    data.update(overrides)
    return data


def test_auth_error_responses_are_generic_and_redacted() -> None:
    client = TestClient(app)

    wrong_username = client.post(
        "/api/auth/login",
        json={"username": "missing_user", "password": "SafePass123"},
    )
    wrong_password = client.post(
        "/api/auth/login",
        json={"username": "safe_creator", "password": SAFE_PASSWORD},
    )

    assert wrong_username.status_code == 401
    assert wrong_password.status_code == 401
    assert wrong_username.json()["detail"] == AUTH_INVALID_CREDENTIALS_MESSAGE
    assert wrong_username.json()["detail"] == wrong_password.json()["detail"]
    assert_text_is_redacted(wrong_username.text)
    assert_text_is_redacted(wrong_password.text)


def test_script_generation_contract_error_response_and_ledger_are_redacted(
    monkeypatch,
    isolated_security_repositories: dict[str, object],
) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "script_generation_mode", "llm")
    monkeypatch.setattr(
        "app.services.script_generation.generator.generate_film_script_adaptation_llm",
        lambda input_data: ShortDramaScriptOutput(
            project_title="旧片场安全样本",
            source_mode="film_script",
            logline="安全虚构 logline。",
            world_setting="安全虚构世界观。",
            characters=[],
            adaptation_notes=None,
            episode_count=1,
            episodes=[
                EpisodeScript(
                    episode_number=1,
                    title="第1集：线索",
                    summary="安全虚构摘要。",
                    hook="安全虚构钩子。",
                    scenes=[],
                )
            ],
            metadata={"generation_mode": "llm"},
        ),
    )
    client = TestClient(app)

    response = client.post("/api/scripts/generate-from-source", json=make_source_request())

    assert response.status_code == 422
    assert response.json()["detail"]["error_code"] == "script_generation_contract_failed"
    assert_text_is_redacted(response.text)

    usage_repository = isolated_security_repositories["usage"]
    stored = usage_repository.get_entry_by_request_id("request_security_contract_failed")
    assert stored is not None
    assert stored.status == "failed"
    assert stored.error_code == "script_generation_contract_failed"
    assert_text_is_redacted(str(stored))


def test_document_import_invalid_docx_error_response_is_redacted() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/documents/import-docx-preview",
        files={
            "file": (
                "safe-invalid.docx",
                b"not a real docx payload",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
        data={
            "request_id": "request_security_invalid_docx",
            "project_id": "project_security_document_import",
            "session_id": "session_security_document_import",
        },
    )

    assert response.status_code == 400
    assert_text_is_redacted(response.text)
    assert "not a real docx payload" not in response.text


def test_document_export_invalid_format_error_response_is_redacted() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/documents/export",
        json={
            "project_title": "安全虚构短剧",
            "content_text": SAFE_CONTENT_TEXT,
            "export_format": "pdf",
            "context_options": {
                "request_id": "request_security_export_invalid",
                "project_id": "project_security_export",
                "session_id": "session_security_export",
            },
        },
    )

    assert response.status_code == 422
    assert_text_is_redacted(response.text)
    assert "content_text" not in response.text


def test_failed_usage_ledger_redacts_provider_response_and_secrets(
    isolated_security_repositories: dict[str, object],
) -> None:
    create_usage_ledger_entry(
        UsageLedgerCreate(
            operation="script_generation",
            status="failed",
            context=ContextOptions(
                request_id="request_security_failed_ledger",
                project_id="project_security_failed_ledger",
                session_id="session_security_failed_ledger",
            ),
            error_code="script_generation_failed",
            error_message=f"{SAFE_PROVIDER_RAW_RESPONSE} /Users/example/private",
            metadata={
                "provider_raw_response": SAFE_PROVIDER_RAW_RESPONSE,
                "api_key": SAFE_API_KEY,
                "password": SAFE_PASSWORD,
                "access_token": SAFE_TOKEN,
                "safe_flag": True,
            },
        )
    )

    usage_repository = isolated_security_repositories["usage"]
    stored = usage_repository.get_entry_by_request_id("request_security_failed_ledger")
    assert stored is not None
    assert stored.error_message_safe == "Sensitive error details redacted."
    assert stored.metadata_json == '{"safe_flag": true}'
    assert_text_is_redacted(str(stored))


def test_ownership_guardrail_error_is_generic_and_redacted(
    isolated_security_repositories: dict[str, object],
) -> None:
    ownership_repository = isolated_security_repositories["ownership"]
    ownership_repository.create_project(
        ProjectRecord(
            id="project_a",
            workspace_id="workspace_a",
            owner_user_id="user_a",
            title="安全测试项目标题不应泄露",
            source_mode="idea",
            status="active",
            created_at=NOW,
            updated_at=NOW,
            last_active_at=NOW,
            metadata_json='{"source_mode":"idea"}',
        )
    )
    ownership_repository.create_session(
        CreativeSessionRecord(
            id="session_a",
            project_id="project_a",
            workspace_id="workspace_a",
            user_id="user_a",
            source_mode="idea",
            context_policy="current_project_only",
            status="active",
            created_at=NOW,
            updated_at=NOW,
            last_event_at=NOW,
            metadata_json='{"context_policy":"current_project_only"}',
        )
    )
    ownership_repository.create_document(
        DocumentRecord(
            id="document_a",
            project_id="project_a",
            session_id="session_a",
            workspace_id="workspace_a",
            user_id="user_a",
            document_type="short_drama_script",
            source_stage="export",
            direction="export",
            filename_safe="safe-private-title.docx",
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            file_size_bytes=2048,
            character_count=None,
            export_format="docx",
            status="exported",
            created_at=NOW,
            metadata_json='{"episode_count":3}',
        )
    )

    with pytest.raises(OwnershipError) as error:
        get_document_for_context(
            "document_a",
            ContextOptions(
                user_id="user_b",
                workspace_id="workspace_b",
                project_id="project_b",
                session_id="session_b",
                context_policy="current_project_only",
            ),
        )

    assert str(error.value) == "Document is not available for the requested context."
    assert "安全测试项目标题不应泄露" not in str(error.value)
    assert "safe-private-title.docx" not in str(error.value)
    assert_text_is_redacted(str(error.value))
