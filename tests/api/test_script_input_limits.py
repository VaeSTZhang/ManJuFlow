from pathlib import Path
import sys

import pytest


API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.services.script_input_limits import (
    MAX_EXTRA_REQUIREMENTS_CHARS,
    MAX_EXTRACTED_TEXT_CHARS,
    MAX_IDEA_TEXT_CHARS,
    MAX_SCRIPT_TEXT_CHARS,
    MAX_SCRIPT_UPLOAD_FILE_SIZE_BYTES,
    count_text_chars,
    is_supported_script_filename,
    validate_extra_requirements,
    validate_extracted_text,
    validate_extracted_text_length,
    validate_idea_text,
    validate_script_filename,
    validate_script_text,
    validate_script_text_length,
    validate_upload_file_size,
)


def test_count_text_chars_returns_length() -> None:
    assert count_text_chars("雨夜重逢") == 4


def test_validate_script_text_length_accepts_max_length() -> None:
    validate_script_text_length("a" * MAX_SCRIPT_TEXT_CHARS)


def test_validate_script_text_length_rejects_over_max_length() -> None:
    with pytest.raises(ValueError, match="SCRIPT_TEXT_TOO_LONG.*100,000"):
        validate_script_text_length("a" * (MAX_SCRIPT_TEXT_CHARS + 1))


def test_validate_extracted_text_length_accepts_max_length() -> None:
    validate_extracted_text_length("a" * MAX_EXTRACTED_TEXT_CHARS)


def test_validate_extracted_text_length_rejects_over_max_length() -> None:
    with pytest.raises(ValueError, match="EXTRACTED_TEXT_TOO_LONG.*100,000"):
        validate_extracted_text_length("a" * (MAX_EXTRACTED_TEXT_CHARS + 1))


def test_validate_upload_file_size_accepts_10mb() -> None:
    validate_upload_file_size(MAX_SCRIPT_UPLOAD_FILE_SIZE_BYTES)


def test_validate_upload_file_size_rejects_over_10mb() -> None:
    with pytest.raises(ValueError, match="UPLOAD_FILE_TOO_LARGE.*10485760"):
        validate_upload_file_size(MAX_SCRIPT_UPLOAD_FILE_SIZE_BYTES + 1)


def test_validate_upload_file_size_rejects_negative_size() -> None:
    with pytest.raises(ValueError, match="UPLOAD_FILE_SIZE_INVALID"):
        validate_upload_file_size(-1)


def test_is_supported_script_filename_accepts_docx() -> None:
    assert is_supported_script_filename("script.docx") is True


def test_is_supported_script_filename_accepts_uppercase_docx() -> None:
    assert is_supported_script_filename("script.DOCX") is True


def test_is_supported_script_filename_rejects_doc() -> None:
    assert is_supported_script_filename("script.doc") is False


def test_validate_script_filename_rejects_doc() -> None:
    with pytest.raises(ValueError, match="UNSUPPORTED_FILE_TYPE.*\\.docx"):
        validate_script_filename("script.doc")


def test_validate_idea_text_accepts_max_length() -> None:
    assert validate_idea_text("a" * MAX_IDEA_TEXT_CHARS) == "a" * MAX_IDEA_TEXT_CHARS


def test_validate_idea_text_rejects_over_max_length() -> None:
    with pytest.raises(ValueError, match="IDEA_TEXT_TOO_LONG.*5,000.*5,001.*1"):
        validate_idea_text("a" * (MAX_IDEA_TEXT_CHARS + 1))


def test_validate_script_text_accepts_max_length() -> None:
    assert validate_script_text("a" * MAX_SCRIPT_TEXT_CHARS) == "a" * MAX_SCRIPT_TEXT_CHARS


def test_validate_script_text_rejects_over_max_length() -> None:
    with pytest.raises(ValueError, match="SCRIPT_TEXT_TOO_LONG.*100,000.*100,001.*1"):
        validate_script_text("a" * (MAX_SCRIPT_TEXT_CHARS + 1))


def test_validate_extracted_text_rejects_over_max_length() -> None:
    with pytest.raises(ValueError, match="EXTRACTED_TEXT_TOO_LONG.*100,000.*100,001.*1"):
        validate_extracted_text("a" * (MAX_EXTRACTED_TEXT_CHARS + 1))


def test_validate_extra_requirements_accepts_none() -> None:
    assert validate_extra_requirements(None) is None


def test_validate_extra_requirements_rejects_over_max_length() -> None:
    with pytest.raises(ValueError, match="EXTRA_REQUIREMENTS_TOO_LONG.*2,000.*2,001.*1"):
        validate_extra_requirements("a" * (MAX_EXTRA_REQUIREMENTS_CHARS + 1))


def test_input_limit_error_does_not_include_full_original_text() -> None:
    oversized_text = "敏感剧本内容" * 500

    with pytest.raises(ValueError) as exc_info:
        validate_extra_requirements(oversized_text)

    assert oversized_text not in str(exc_info.value)
