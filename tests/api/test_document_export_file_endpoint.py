from io import BytesIO
from pathlib import Path
import sys
from zipfile import ZipFile

from fastapi.testclient import TestClient
import pytest


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.repositories.ownership_repository import SQLiteOwnershipRepository  # noqa: E402
from app.repositories.usage_ledger_repository import SQLiteUsageLedgerRepository  # noqa: E402
from app.main import app  # noqa: E402
from app.services.ownership_service import (  # noqa: E402
    configure_ownership_repository_for_testing,
    reset_ownership_repository_for_testing,
)
from app.services.usage_ledger_service import (  # noqa: E402
    configure_usage_ledger_repository_for_testing,
    reset_usage_ledger_repository_for_testing,
)


DOCX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


@pytest.fixture(autouse=True)
def isolated_usage_ledger_repository(tmp_path: Path):
    usage_repository = SQLiteUsageLedgerRepository(tmp_path / "document_export_file_endpoint_test.sqlite")
    ownership_repository = SQLiteOwnershipRepository(tmp_path / "document_export_file_endpoint_ownership.sqlite")
    configure_usage_ledger_repository_for_testing(usage_repository)
    configure_ownership_repository_for_testing(ownership_repository)
    yield usage_repository
    reset_usage_ledger_repository_for_testing()
    reset_ownership_repository_for_testing()


def make_docx_export_request(**overrides) -> dict:
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
        "metadata": {"edited": True},
    }
    data.update(overrides)
    return data


def read_docx_document_xml(docx_bytes: bytes) -> str:
    with ZipFile(BytesIO(docx_bytes)) as archive:
        return archive.read("word/document.xml").decode("utf-8")


def test_export_file_endpoint_returns_200() -> None:
    client = TestClient(app)

    response = client.post("/api/documents/export-file", json=make_docx_export_request())

    assert response.status_code == 200


def test_export_file_endpoint_returns_docx_content_type() -> None:
    client = TestClient(app)

    response = client.post("/api/documents/export-file", json=make_docx_export_request())

    assert response.status_code == 200
    assert DOCX_MEDIA_TYPE in response.headers["content-type"]


def test_export_file_endpoint_content_disposition_is_attachment_docx() -> None:
    client = TestClient(app)

    response = client.post("/api/documents/export-file", json=make_docx_export_request())
    content_disposition = response.headers["content-disposition"]

    assert response.status_code == 200
    assert "attachment" in content_disposition
    assert ".docx" in content_disposition


def test_export_file_endpoint_response_content_is_valid_docx_zip() -> None:
    client = TestClient(app)

    response = client.post("/api/documents/export-file", json=make_docx_export_request())

    with ZipFile(BytesIO(response.content)) as archive:
        assert "word/document.xml" in archive.namelist()


def test_export_file_endpoint_document_xml_contains_title() -> None:
    client = TestClient(app)

    response = client.post("/api/documents/export-file", json=make_docx_export_request())
    document_xml = read_docx_document_xml(response.content)

    assert "测试短剧：灯火归来" in document_xml


def test_export_file_endpoint_document_xml_contains_character_or_episode() -> None:
    client = TestClient(app)

    response = client.post("/api/documents/export-file", json=make_docx_export_request())
    document_xml = read_docx_document_xml(response.content)

    assert "林灯" in document_xml
    assert "灯火重启" in document_xml


def test_export_file_endpoint_rejects_non_docx_format() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/documents/export-file",
        json=make_docx_export_request(export_format="txt", content_text="测试内容", structured_payload=None),
    )

    assert response.status_code == 400
    assert "export_format='docx'" in response.json()["detail"]


def test_export_file_endpoint_keeps_safe_filename_in_content_disposition() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/documents/export-file",
        json=make_docx_export_request(filename="/Users/example/secret/script.txt"),
    )
    content_disposition = response.headers["content-disposition"]

    assert response.status_code == 200
    assert "script.docx" in content_disposition
    assert "/Users" not in content_disposition
    assert "/" not in content_disposition
    assert "\\" not in content_disposition


def test_export_file_endpoint_response_does_not_include_path_like_fields() -> None:
    client = TestClient(app)

    response = client.post("/api/documents/export-file", json=make_docx_export_request())
    document_xml = read_docx_document_xml(response.content)

    assert response.status_code == 200
    assert "server_path" not in document_xml
    assert "local_path" not in document_xml
    assert "absolute_path" not in document_xml
    assert "/Users/example" not in document_xml


def test_openapi_contains_export_file_route() -> None:
    client = TestClient(app)

    response = client.get("/openapi.json")
    data = response.json()

    assert response.status_code == 200
    assert "/api/documents/export-file" in data["paths"]
