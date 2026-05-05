from io import BytesIO
from pathlib import Path
import sys

from docx import Document
from fastapi.testclient import TestClient


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(API_ROOT))

from app.main import app  # noqa: E402


DOCX_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def build_safe_docx_bytes(paragraphs: list[str]) -> bytes:
    document = Document()
    for paragraph in paragraphs:
        document.add_paragraph(paragraph)

    buffer = BytesIO()
    document.save(buffer)
    return buffer.getvalue()


def collect_storage_files() -> set[str]:
    storage_roots = [
        PROJECT_ROOT / "uploads",
        PROJECT_ROOT / "apps" / "api" / "uploads",
        PROJECT_ROOT / "storage",
        PROJECT_ROOT / "apps" / "api" / "app" / "storage",
    ]
    files: set[str] = set()
    for root in storage_roots:
        if root.exists():
            files.update(str(path.relative_to(PROJECT_ROOT)) for path in root.rglob("*") if path.is_file())
    return files


def make_docx_upload(filename: str = "old-cinema.docx", paragraphs: list[str] | None = None) -> dict:
    file_bytes = build_safe_docx_bytes(
        paragraphs
        or [
            "旧影院来信",
            "放映员在拆迁前夜收到一封未来来信。",
            "午夜最后一场电影让旧案重新浮出水面。",
        ]
    )
    return {"file": (filename, file_bytes, DOCX_CONTENT_TYPE)}


def test_import_docx_preview_endpoint_returns_200() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/documents/import-docx-preview",
        files=make_docx_upload(),
        data={"project_title": "旧影院来信"},
    )

    assert response.status_code == 200


def test_import_docx_preview_endpoint_returns_extracted_text_and_safe_filename() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/documents/import-docx-preview",
        files=make_docx_upload(filename="/Users/example/secret/old-cinema.docx"),
        data={"project_title": "旧影院来信"},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["status"] == "preview_ready"
    assert data["preview"]["source"]["filename"] == "old-cinema.docx"
    assert data["preview"]["source"]["source_type"] == "docx"
    assert "放映员在拆迁前夜" in data["preview"]["extracted_text"]
    assert "/Users/example/secret" not in str(data)


def test_import_docx_preview_endpoint_returns_context_options() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/documents/import-docx-preview",
        files=make_docx_upload(),
        data={
            "project_title": "旧影院来信",
            "user_id": "internal_user_mock_001",
            "workspace_id": "workspace_dramora_internal",
            "project_id": "project_docx_import_endpoint",
            "session_id": "session_docx_import_endpoint",
            "request_id": "request_docx_import_endpoint",
            "source_stage": "imported_document",
            "context_policy": "current_project_only",
        },
    )
    data = response.json()

    assert response.status_code == 200
    assert data["context_options"]["project_id"] == "project_docx_import_endpoint"
    assert data["context_options"]["session_id"] == "session_docx_import_endpoint"
    assert data["context_options"]["source_stage"] == "imported_document"
    assert data["context_options"]["context_policy"] == "current_project_only"


def test_import_docx_preview_endpoint_rejects_empty_file() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/documents/import-docx-preview",
        files={"file": ("empty.docx", b"", DOCX_CONTENT_TYPE)},
    )

    assert response.status_code == 400
    assert "DOCX 文件内容为空" in response.text


def test_import_docx_preview_endpoint_rejects_invalid_docx_bytes() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/documents/import-docx-preview",
        files={"file": ("broken.docx", b"not a docx package", DOCX_CONTENT_TYPE)},
    )

    assert response.status_code == 400
    assert "无法解析 DOCX 文档" in response.text


def test_import_docx_preview_endpoint_rejects_non_docx_filename() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/documents/import-docx-preview",
        files={"file": ("source.txt", b"safe text", "text/plain")},
    )

    assert response.status_code == 400
    assert ".docx" in response.text


def test_import_docx_preview_endpoint_rejects_obviously_wrong_content_type() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/documents/import-docx-preview",
        files={"file": ("source.docx", b"safe text", "text/plain")},
    )

    assert response.status_code == 400
    assert "DOCX" in response.text


def test_import_docx_preview_endpoint_does_not_save_files_to_local_storage() -> None:
    client = TestClient(app)
    before_files = collect_storage_files()

    response = client.post("/api/documents/import-docx-preview", files=make_docx_upload())

    after_files = collect_storage_files()
    assert response.status_code == 200
    assert after_files == before_files


def test_import_docx_preview_endpoint_response_does_not_leak_local_paths() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/documents/import-docx-preview",
        files=make_docx_upload(filename="/Users/example/private/source.docx"),
    )
    response_text = response.text

    assert response.status_code == 200
    assert "/Users/example/private" not in response_text
    assert "server_path" not in response_text
    assert "local_path" not in response_text
    assert "absolute_path" not in response_text


def test_openapi_contains_import_docx_preview_route() -> None:
    client = TestClient(app)

    response = client.get("/openapi.json")
    data = response.json()

    assert response.status_code == 200
    assert "/api/documents/import-docx-preview" in data["paths"]
