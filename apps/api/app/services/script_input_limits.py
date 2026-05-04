MAX_IDEA_TEXT_CHARS = 5_000
MAX_EXTRA_REQUIREMENTS_CHARS = 2_000
MAX_SCRIPT_TEXT_CHARS = 100_000
MAX_EXTRACTED_TEXT_CHARS = 100_000
MAX_SCRIPT_UPLOAD_FILE_SIZE_BYTES = 10 * 1024 * 1024
DEFAULT_SCRIPT_CHUNK_SIZE_CHARS = 8_000
DEFAULT_SCRIPT_CHUNK_OVERLAP_CHARS = 400
SUPPORTED_SCRIPT_UPLOAD_EXTENSIONS = (".docx",)


def count_text_chars(text: str) -> int:
    return len(text)


def validate_text_length(value: str | None, max_chars: int, field_label: str, error_code: str) -> str | None:
    if value is None:
        return None

    text_length = count_text_chars(value)
    if text_length > max_chars:
        exceeded_chars = text_length - max_chars
        raise ValueError(
            f"{error_code}: {field_label}已超出 {max_chars:,} 字，"
            f"当前 {text_length:,} 字，请删减 {exceeded_chars:,} 字后再提交。"
        )

    return value


def validate_idea_text(text: str) -> str:
    return validate_text_length(
        text,
        MAX_IDEA_TEXT_CHARS,
        "灵感内容",
        "IDEA_TEXT_TOO_LONG",
    ) or ""


def validate_extra_requirements(text: str | None) -> str | None:
    return validate_text_length(
        text,
        MAX_EXTRA_REQUIREMENTS_CHARS,
        "额外要求",
        "EXTRA_REQUIREMENTS_TOO_LONG",
    )


def validate_script_text_length(text: str, max_chars: int = MAX_SCRIPT_TEXT_CHARS) -> None:
    validate_text_length(text, max_chars, "已有剧本文本", "SCRIPT_TEXT_TOO_LONG")


def validate_script_text(text: str | None) -> str | None:
    return validate_text_length(
        text,
        MAX_SCRIPT_TEXT_CHARS,
        "已有剧本文本",
        "SCRIPT_TEXT_TOO_LONG",
    )


def validate_extracted_text_length(text: str, max_chars: int = MAX_EXTRACTED_TEXT_CHARS) -> None:
    validate_text_length(text, max_chars, "提取文本", "EXTRACTED_TEXT_TOO_LONG")


def validate_extracted_text(text: str | None) -> str | None:
    return validate_text_length(
        text,
        MAX_EXTRACTED_TEXT_CHARS,
        "提取文本",
        "EXTRACTED_TEXT_TOO_LONG",
    )


def validate_upload_file_size(
    file_size: int,
    max_bytes: int = MAX_SCRIPT_UPLOAD_FILE_SIZE_BYTES,
) -> None:
    if file_size < 0:
        raise ValueError("UPLOAD_FILE_SIZE_INVALID: file_size must be greater than or equal to 0.")

    if file_size > max_bytes:
        raise ValueError(
            f"UPLOAD_FILE_TOO_LARGE: file_size {file_size} exceeds max_bytes {max_bytes}."
        )


def is_supported_script_filename(filename: str) -> bool:
    normalized_filename = filename.strip().lower()
    return normalized_filename.endswith(SUPPORTED_SCRIPT_UPLOAD_EXTENSIONS)


def validate_script_filename(filename: str) -> None:
    if not is_supported_script_filename(filename):
        supported_extensions = ", ".join(SUPPORTED_SCRIPT_UPLOAD_EXTENSIONS)
        raise ValueError(
            f"UNSUPPORTED_FILE_TYPE: only {supported_extensions} script uploads are supported."
        )
