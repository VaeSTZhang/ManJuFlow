import hashlib
import re

from app.schemas.upload import ScriptUploadOutput, UploadSourceInput, UploadSourceMetadata
from app.services.script_input_limits import (
    validate_extracted_text,
    validate_extra_requirements,
    validate_upload_file_size,
)


DOCX_UPLOAD_WARNING = "Only .docx is planned for the first production-ready upload flow."


def _slugify_text(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    return slug or "script"


def generate_mock_source_id(project_title: str, original_filename: str) -> str:
    raw_value = f"{project_title.strip()}::{original_filename.strip()}"
    short_hash = hashlib.sha256(raw_value.encode("utf-8")).hexdigest()[:10]
    filename_slug = _slugify_text(original_filename.rsplit(".", 1)[0])[:24]
    return f"mock_upload_{filename_slug}_{short_hash}"


def extract_script_text_mock(original_filename: str, source_type: str = "script_docx") -> str:
    return (
        f"Mock extracted script text from {source_type}: {original_filename}。\n"
        "第1集 第1场｜医院门口｜雨夜。暴雨中，林晚撑着黑伞站在医院门口，"
        "顾沉从车里下来，两人隔雨对视。\n"
        "顾沉：你终于肯回来了？\n"
        "林晚：我回来，不是为了见你。"
    )


def create_script_upload_mock(
    input_data: UploadSourceInput,
    original_filename: str = "mock_script.docx",
    content_type: str = "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    file_size: int = 1024,
) -> ScriptUploadOutput:
    validate_extra_requirements(input_data.extra_requirements)
    validate_upload_file_size(file_size)

    source_id = generate_mock_source_id(input_data.project_title, original_filename)
    extracted_text = extract_script_text_mock(original_filename, input_data.source_type)
    validate_extracted_text(extracted_text)
    warnings = []

    if not original_filename.lower().endswith(".docx"):
        warnings.append(DOCX_UPLOAD_WARNING)

    metadata = UploadSourceMetadata(
        source_id=source_id,
        project_title=input_data.project_title,
        project_id=input_data.project_id,
        workspace_id=input_data.workspace_id,
        user_id=input_data.user_id,
        ai_account_id=input_data.ai_account_id,
        original_filename=original_filename,
        content_type=content_type,
        file_size=file_size,
        sha256=None,
        storage_path=None,
        source_type=input_data.source_type,
        extraction_status="succeeded",
        extracted_text_length=len(extracted_text),
        metadata={
            "language": input_data.language,
            "generation_mode": "mock",
            "upload_policy": "metadata_only_no_real_file_saved",
            "context_policy": "current_project_only",
        },
    )

    return ScriptUploadOutput(
        source_id=source_id,
        project_title=input_data.project_title,
        extracted_text=extracted_text,
        metadata=metadata,
        warnings=warnings,
    )
