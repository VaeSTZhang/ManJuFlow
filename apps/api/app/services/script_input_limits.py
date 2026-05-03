MAX_SCRIPT_TEXT_CHARS = 100_000
MAX_EXTRACTED_TEXT_CHARS = 100_000
MAX_SCRIPT_UPLOAD_FILE_SIZE_BYTES = 10 * 1024 * 1024
DEFAULT_SCRIPT_CHUNK_SIZE_CHARS = 8_000
DEFAULT_SCRIPT_CHUNK_OVERLAP_CHARS = 400
SUPPORTED_SCRIPT_UPLOAD_EXTENSIONS = (".docx",)


def count_text_chars(text: str) -> int:
    return len(text)


def validate_script_text_length(text: str, max_chars: int = MAX_SCRIPT_TEXT_CHARS) -> None:
    text_length = count_text_chars(text)
    if text_length > max_chars:
        raise ValueError(
            f"SCRIPT_TEXT_TOO_LONG: script_text length {text_length} exceeds max_chars {max_chars}."
        )


def validate_extracted_text_length(text: str, max_chars: int = MAX_EXTRACTED_TEXT_CHARS) -> None:
    text_length = count_text_chars(text)
    if text_length > max_chars:
        raise ValueError(
            f"EXTRACTED_TEXT_TOO_LONG: extracted_text length {text_length} exceeds max_chars {max_chars}."
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
