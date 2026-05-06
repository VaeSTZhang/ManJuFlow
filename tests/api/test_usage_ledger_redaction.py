from pathlib import Path
import sys

import pytest


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.repositories.usage_ledger_repository import SQLiteUsageLedgerRepository  # noqa: E402
from app.schemas.context import ContextOptions  # noqa: E402
from app.schemas.document import DocumentExportInput  # noqa: E402
from app.schemas.script import CharacterProfile, DialogueLine, EpisodeScript, SceneScript  # noqa: E402
from app.schemas.script_generation import (  # noqa: E402
    AIRequestOptions,
    ShortDramaGenerationInput,
    ShortDramaScriptOutput,
)
from app.schemas.usage_ledger import UsageLedgerCreate  # noqa: E402
from app.services.document_docx_export_service import build_docx_export_bytes  # noqa: E402
from app.services.document_export_service import export_document  # noqa: E402
from app.services.document_import_service import build_document_import_preview  # noqa: E402
from app.services.script_generation.usage_ledger import attach_usage_ledger_metadata  # noqa: E402
from app.services.usage_ledger_service import (  # noqa: E402
    configure_usage_ledger_repository_for_testing,
    create_usage_ledger_entry,
    reset_usage_ledger_repository_for_testing,
)


SAFE_SOURCE_TEXT = "旧楼完整输入正文不应进入用量记录。"
SAFE_GENERATED_TEXT = "完整生成剧本文本不应进入用量记录。"
SAFE_UPLOAD_TEXT = "完整上传文档正文不应进入用量记录。"
SAFE_EXPORT_TEXT = "完整导出文本不应进入用量记录。"
SAFE_PROVIDER_RESPONSE = "provider 原始响应不应进入用量记录。"
SAFE_API_KEY = "not-a-real-api-key"
SAFE_PASSWORD = "NotRealPass123"
SAFE_PASSWORD_HASH = "not-a-real-password-hash"
SAFE_ACCESS_TOKEN = "not-a-real-access-token"
SAFE_SESSION_TOKEN = "not-a-real-session-token"
SAFE_LOCAL_PATH = "/Users/example/private/source.docx"

FORBIDDEN_LEDGER_VALUES = [
    SAFE_SOURCE_TEXT,
    SAFE_GENERATED_TEXT,
    SAFE_UPLOAD_TEXT,
    SAFE_EXPORT_TEXT,
    SAFE_PROVIDER_RESPONSE,
    SAFE_API_KEY,
    SAFE_PASSWORD,
    SAFE_PASSWORD_HASH,
    SAFE_ACCESS_TOKEN,
    SAFE_SESSION_TOKEN,
    SAFE_LOCAL_PATH,
    "extracted_text",
    "preview_text",
    "docx_bytes",
    "provider_raw_response",
    "api_key",
    "password_hash",
    "access_token",
    "session_token",
]


@pytest.fixture(autouse=True)
def isolated_usage_ledger_repository(tmp_path: Path):
    repository = SQLiteUsageLedgerRepository(tmp_path / "usage_ledger_redaction_test.sqlite")
    configure_usage_ledger_repository_for_testing(repository)
    yield repository
    reset_usage_ledger_repository_for_testing()


def assert_record_is_redacted(record_text: str) -> None:
    for forbidden_value in FORBIDDEN_LEDGER_VALUES:
        assert forbidden_value not in record_text


def make_context(request_id: str) -> ContextOptions:
    return ContextOptions(
        user_id="user_safe_creator_001",
        workspace_id="workspace_dramora_internal",
        project_id="project_redaction_test",
        session_id="session_redaction_test",
        request_id=request_id,
        source_stage="generated_script",
    )


def make_short_drama_output() -> ShortDramaScriptOutput:
    return ShortDramaScriptOutput(
        project_title="测试短剧：旧楼灯火",
        source_mode="idea",
        logline=SAFE_GENERATED_TEXT,
        world_setting="安全虚构世界观。",
        characters=[
            CharacterProfile(
                name="林灯",
                role="主角",
                age="28",
                personality="冷静敏锐。",
                arc="从逃避到面对真相。",
            )
        ],
        episode_count=1,
        episodes=[
            EpisodeScript(
                episode_number=1,
                title="灯火重启",
                summary="林灯回到旧楼。",
                hook="剧本最后一页出现她的名字。",
                scenes=[
                    SceneScript(
                        scene_number=1,
                        location="旧楼走廊",
                        time="夜",
                        description="走廊尽头亮着灯。",
                        dialogues=[
                            DialogueLine(character="林灯", line="这不是我的台词。")
                        ],
                        visual_notes="冷色灯光。",
                        emotion_curve="疑惑到紧张。",
                    )
                ],
            )
        ],
        metadata={"generation_mode": "mock", "provider": "deepseek", "model": "deepseek-chat"},
    )


def test_script_generation_usage_ledger_does_not_store_full_input_or_output(
    isolated_usage_ledger_repository: SQLiteUsageLedgerRepository,
) -> None:
    input_data = ShortDramaGenerationInput(
        source_mode="idea",
        idea_text=SAFE_SOURCE_TEXT,
        target_episode_count=1,
        ai_options=AIRequestOptions(provider="deepseek", model="deepseek-chat"),
        context_options=make_context("request_script_redaction"),
    )

    output = attach_usage_ledger_metadata(make_short_drama_output(), input_data)
    stored = isolated_usage_ledger_repository.get_entry_by_request_id("request_script_redaction")

    assert stored is not None
    assert stored.metadata_json is not None
    assert SAFE_SOURCE_TEXT not in stored.metadata_json
    assert SAFE_GENERATED_TEXT not in stored.metadata_json
    assert SAFE_SOURCE_TEXT not in str(output.metadata["usage_ledger"])
    assert SAFE_GENERATED_TEXT not in str(output.metadata["usage_ledger"])


def test_document_import_usage_ledger_does_not_store_extracted_or_preview_text(
    isolated_usage_ledger_repository: SQLiteUsageLedgerRepository,
) -> None:
    build_document_import_preview(
        filename="safe-import.docx",
        extracted_text=SAFE_UPLOAD_TEXT,
        file_size_bytes=2048,
        context_options=make_context("request_import_redaction"),
    )
    stored = isolated_usage_ledger_repository.get_entry_by_request_id("request_import_redaction")

    assert stored is not None
    assert stored.metadata_json is not None
    assert "document_operation" in stored.metadata_json
    assert SAFE_UPLOAD_TEXT not in stored.metadata_json
    assert "extracted_text" not in stored.metadata_json
    assert "preview_text" not in stored.metadata_json


def test_document_export_txt_usage_ledger_does_not_store_full_content_text(
    isolated_usage_ledger_repository: SQLiteUsageLedgerRepository,
) -> None:
    export_document(
        DocumentExportInput(
            project_title="测试短剧：旧楼灯火",
            content_text=SAFE_EXPORT_TEXT,
            export_format="txt",
            context_options=make_context("request_export_txt_redaction"),
        )
    )
    stored = isolated_usage_ledger_repository.get_entry_by_request_id("request_export_txt_redaction")

    assert stored is not None
    assert stored.metadata_json is not None
    assert SAFE_EXPORT_TEXT not in stored.metadata_json
    assert "content_text" not in stored.metadata_json


def test_document_export_docx_usage_ledger_does_not_store_docx_bytes(
    isolated_usage_ledger_repository: SQLiteUsageLedgerRepository,
) -> None:
    docx_bytes = build_docx_export_bytes(
        DocumentExportInput(
            project_title="测试短剧：旧楼灯火",
            structured_payload={
                "project_title": "测试短剧：旧楼灯火",
                "logline": SAFE_EXPORT_TEXT,
                "characters": [{"name": "林灯"}],
                "episodes": [{"episode_number": 1, "title": "灯火重启"}],
            },
            export_format="docx",
            context_options=make_context("request_export_docx_redaction"),
        )
    )
    stored = isolated_usage_ledger_repository.get_entry_by_request_id("request_export_docx_redaction")

    assert len(docx_bytes) > 0
    assert stored is not None
    assert stored.metadata_json is not None
    assert "docx_bytes" not in stored.metadata_json
    assert "PK" not in stored.metadata_json
    assert SAFE_EXPORT_TEXT not in stored.metadata_json


def test_failed_usage_ledger_filters_secret_keys_and_local_path_values(
    isolated_usage_ledger_repository: SQLiteUsageLedgerRepository,
) -> None:
    create_usage_ledger_entry(
        UsageLedgerCreate(
            operation="script_generation",
            status="failed",
            context=make_context("request_failed_redaction"),
            error_code="script_generation_failed",
            error_message=f"provider_raw_response contains {SAFE_LOCAL_PATH}",
            metadata={
                "source_text": SAFE_SOURCE_TEXT,
                "extracted_text": SAFE_UPLOAD_TEXT,
                "preview_text": SAFE_UPLOAD_TEXT,
                "docx_bytes": "PK docx bytes placeholder",
                "provider_raw_response": SAFE_PROVIDER_RESPONSE,
                "api_key": SAFE_API_KEY,
                "password": SAFE_PASSWORD,
                "password_hash": SAFE_PASSWORD_HASH,
                "access_token": SAFE_ACCESS_TOKEN,
                "session_token": SAFE_SESSION_TOKEN,
                "path_note": SAFE_LOCAL_PATH,
                "safe_flag": True,
            },
        )
    )
    stored = isolated_usage_ledger_repository.get_entry_by_request_id("request_failed_redaction")

    assert stored is not None
    assert stored.error_message_safe == "Sensitive error details redacted."
    assert stored.metadata_json == '{"safe_flag": true}'
    assert_record_is_redacted(str(stored))
