from pathlib import Path
import json
import sys

import pytest


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.schemas.document import DocumentExportInput, DocumentExportOutput
from app.services.document_export_service import (
    DOCX_EXPORT_NOT_IMPLEMENTED_MESSAGE,
    build_json_export_content,
    build_safe_export_filename,
    build_txt_export_content,
    export_document,
)


def test_export_document_txt_returns_document_export_output() -> None:
    output = export_document(
        DocumentExportInput(
            project_title="测试短剧：灯火归来",
            content_text="第一集：旧楼重逢。",
            export_format="txt",
        )
    )

    assert isinstance(output, DocumentExportOutput)
    assert output.project_title == "测试短剧：灯火归来"
    assert output.export_format == "txt"
    assert output.download_url is None


def test_txt_export_content_contains_project_title_and_body() -> None:
    content = build_txt_export_content(
        DocumentExportInput(
            project_title="测试短剧：灯火归来",
            content_text="林灯回到旧楼，发现父亲留下的剧本。",
            export_format="txt",
        )
    )

    assert "测试短剧：灯火归来" in content
    assert "林灯回到旧楼" in content


def test_json_export_content_uses_structured_payload() -> None:
    content = build_json_export_content(
        DocumentExportInput(
            project_title="测试短剧：灯火归来",
            structured_payload={
                "project_title": "测试短剧：灯火归来",
                "episodes": [{"episode_number": 1, "title": "旧楼灯火"}],
            },
            export_format="json",
        )
    )

    parsed = json.loads(content)
    assert parsed["project_title"] == "测试短剧：灯火归来"
    assert parsed["episodes"][0]["title"] == "旧楼灯火"


def test_json_export_keeps_chinese_readable() -> None:
    content = build_json_export_content(
        DocumentExportInput(
            project_title="测试短剧：灯火归来",
            structured_payload={"logline": "年轻编剧回到旧楼。"},
            export_format="json",
        )
    )

    assert "年轻编剧回到旧楼" in content
    assert "\\u" not in content


def test_safe_export_filename_strips_paths_and_uses_matching_suffix() -> None:
    filename = build_safe_export_filename(
        DocumentExportInput(
            project_title="测试短剧：灯火归来",
            content_text="测试内容",
            export_format="txt",
            filename="/Users/example/Desktop/secret/script.docx",
        )
    )

    assert filename == "script.txt"
    assert "/Users" not in filename
    assert "/" not in filename
    assert "\\" not in filename


def test_export_document_sets_file_size_bytes() -> None:
    output = export_document(
        DocumentExportInput(
            project_title="测试短剧：灯火归来",
            content_text="测试内容",
            export_format="txt",
        )
    )

    assert output.file_size_bytes is not None
    assert output.file_size_bytes > 0


def test_export_document_metadata_contains_safe_tracking_fields() -> None:
    output = export_document(
        DocumentExportInput(
            project_title="测试短剧：灯火归来",
            document_type="short_drama_script",
            source_stage="script",
            content_text="测试内容",
            export_format="txt",
            metadata={"edited": True},
        )
    )

    assert output.metadata["edited"] is True
    assert output.metadata["export_format"] == "txt"
    assert output.metadata["source_stage"] == "script"
    assert output.metadata["document_type"] == "short_drama_script"
    assert output.metadata["content_source"] == "content_text"


def test_export_document_docx_returns_clear_not_implemented_error() -> None:
    with pytest.raises(ValueError, match=DOCX_EXPORT_NOT_IMPLEMENTED_MESSAGE):
        export_document(
            DocumentExportInput(
                project_title="测试短剧：灯火归来",
                content_text="测试内容",
                export_format="docx",
            )
        )


def test_export_document_model_dump_does_not_include_local_path_fields() -> None:
    output = export_document(
        DocumentExportInput(
            project_title="测试短剧：灯火归来",
            structured_payload={
                "project_title": "测试短剧：灯火归来",
                "server_path": "/Users/example/Desktop/secret",
                "nested": {"local_path": "/tmp/secret"},
            },
            export_format="json",
            metadata={
                "absolute_path": "/Users/example/Desktop/secret",
                "source": "test",
            },
        )
    )

    dumped = output.model_dump()
    dumped_text = json.dumps(dumped, ensure_ascii=False)

    assert "server_path" not in dumped_text
    assert "local_path" not in dumped_text
    assert "absolute_path" not in dumped_text
    assert "/Users/example" not in dumped_text
