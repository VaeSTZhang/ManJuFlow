from io import BytesIO
from pathlib import Path
import sys
from zipfile import ZipFile

import pytest


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.repositories.usage_ledger_repository import SQLiteUsageLedgerRepository
from app.repositories.ownership_repository import SQLiteOwnershipRepository
from app.schemas.document import DocumentExportInput
from app.services.document_docx_export_service import (
    build_docx_export_bytes,
    sanitize_docx_filename,
)
from app.services.usage_ledger_service import (
    configure_usage_ledger_repository_for_testing,
    reset_usage_ledger_repository_for_testing,
)
from app.services.ownership_service import (
    configure_ownership_repository_for_testing,
    reset_ownership_repository_for_testing,
)


@pytest.fixture(autouse=True)
def isolated_usage_ledger_repository(tmp_path: Path):
    usage_repository = SQLiteUsageLedgerRepository(tmp_path / "document_docx_export_service_test.sqlite")
    ownership_repository = SQLiteOwnershipRepository(tmp_path / "document_docx_export_ownership_test.sqlite")
    configure_usage_ledger_repository_for_testing(usage_repository)
    configure_ownership_repository_for_testing(ownership_repository)
    yield usage_repository
    reset_usage_ledger_repository_for_testing()
    reset_ownership_repository_for_testing()


def make_short_drama_export_input(**overrides) -> DocumentExportInput:
    payload = {
        "project_title": "测试短剧：灯火归来",
        "source_mode": "idea",
        "logline": "年轻编剧回到旧楼，在层层反转中找回父亲留下的最后一场戏。",
        "world_setting": "当代都市旧楼即将拆迁，所有角色都被一份未完成剧本重新牵连。",
        "characters": [
            {
                "name": "林灯",
                "role": "主角",
                "age": "28",
                "personality": "冷静、敏锐，习惯用剧本逻辑拆解现实冲突。",
                "arc": "从逃避旧楼真相，到主动完成父亲留下的最后一场戏。",
            }
        ],
        "adaptation_notes": {
            "adaptation_strategy": "强化旧楼悬疑线和人物反转。",
            "preserved_elements": ["旧楼", "父亲留下的剧本"],
            "changed_elements": ["弱化支线人物"],
            "short_drama_hooks": ["每集结尾给出新线索"],
            "risk_notes": ["避免对白过长"],
        },
        "episode_count": 1,
        "episodes": [
            {
                "episode_number": 1,
                "title": "灯火重启",
                "summary": "林灯回到旧楼后，发现父亲留下的剧本与拆迁名单同时指向同一个秘密。",
                "hook": "她翻到最后一页，发现下一场戏的主角写着自己的名字。",
                "scenes": [
                    {
                        "scene_number": 1,
                        "location": "旧楼走廊",
                        "time": "夜",
                        "description": "停电后的走廊里，只有尽头办公室亮着灯。",
                        "dialogues": [
                            {
                                "character": "林灯",
                                "line": "这栋楼不是早就没人了吗？",
                            }
                        ],
                        "visual_notes": "冷色灯光，长走廊压迫感。",
                        "emotion_curve": "疑惑到紧张。",
                    }
                ],
            }
        ],
        "metadata": {
            "server_path": "/Users/example/secret",
            "local_path": "/tmp/secret",
            "absolute_path": "/Users/example/secret/script.docx",
        },
    }
    data = {
        "project_title": "测试短剧：灯火归来",
        "document_type": "short_drama_script",
        "source_stage": "script",
        "structured_payload": payload,
        "export_format": "docx",
        "filename": "dramora-short-drama-script.docx",
    }
    data.update(overrides)
    return DocumentExportInput(**data)


def read_docx_document_xml(docx_bytes: bytes) -> str:
    with ZipFile(BytesIO(docx_bytes)) as archive:
        return archive.read("word/document.xml").decode("utf-8")


def test_build_docx_export_bytes_returns_bytes() -> None:
    docx_bytes = build_docx_export_bytes(make_short_drama_export_input())

    assert isinstance(docx_bytes, bytes)


def test_build_docx_export_bytes_has_content() -> None:
    docx_bytes = build_docx_export_bytes(make_short_drama_export_input())

    assert len(docx_bytes) > 0


def test_build_docx_export_bytes_is_valid_docx_zip() -> None:
    docx_bytes = build_docx_export_bytes(make_short_drama_export_input())

    with ZipFile(BytesIO(docx_bytes)) as archive:
        assert "word/document.xml" in archive.namelist()


def test_docx_document_xml_contains_safe_fixture_title() -> None:
    document_xml = read_docx_document_xml(build_docx_export_bytes(make_short_drama_export_input()))

    assert "测试短剧：灯火归来" in document_xml


def test_docx_document_xml_contains_logline() -> None:
    document_xml = read_docx_document_xml(build_docx_export_bytes(make_short_drama_export_input()))

    assert "年轻编剧回到旧楼" in document_xml


def test_docx_document_xml_contains_character_name() -> None:
    document_xml = read_docx_document_xml(build_docx_export_bytes(make_short_drama_export_input()))

    assert "林灯" in document_xml


def test_docx_document_xml_contains_episode_title() -> None:
    document_xml = read_docx_document_xml(build_docx_export_bytes(make_short_drama_export_input()))

    assert "灯火重启" in document_xml


def test_sanitize_docx_filename_strips_paths_and_rewrites_suffix() -> None:
    filename = sanitize_docx_filename("/Users/example/secret/script.txt", "测试短剧：灯火归来")

    assert filename == "script.docx"
    assert "/Users" not in filename
    assert "/" not in filename
    assert "\\" not in filename


def test_sanitize_docx_filename_uses_project_title_when_filename_empty() -> None:
    filename = sanitize_docx_filename(None, "测试短剧：灯火归来")

    assert filename == "测试短剧-灯火归来.docx"


def test_build_docx_export_bytes_rejects_non_docx_format() -> None:
    with pytest.raises(ValueError, match="export_format='docx'"):
        build_docx_export_bytes(
            make_short_drama_export_input(
                export_format="txt",
                content_text="测试内容",
                structured_payload=None,
            )
        )


def test_build_docx_export_bytes_does_not_write_docx_to_disk(tmp_path: Path) -> None:
    before = set(tmp_path.glob("*.docx"))

    build_docx_export_bytes(make_short_drama_export_input())

    after = set(tmp_path.glob("*.docx"))
    assert after == before


def test_docx_document_xml_does_not_include_path_like_fields() -> None:
    document_xml = read_docx_document_xml(build_docx_export_bytes(make_short_drama_export_input()))

    assert "server_path" not in document_xml
    assert "local_path" not in document_xml
    assert "absolute_path" not in document_xml
    assert "/Users/example" not in document_xml
