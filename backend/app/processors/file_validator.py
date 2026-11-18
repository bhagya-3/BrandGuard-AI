
from pathlib import Path

from app.processors.format_detector import (
    detect_format,
    FormatDetectionError,
)


MAX_FILE_SIZE_MB = 25
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


class FileValidationError(ValueError):
    pass


def validate_file(filename: str, content: bytes) -> dict:
    if not filename or not filename.strip():
        raise FileValidationError("Filename is required.")

    if not content:
        raise FileValidationError("Uploaded file is empty.")

    if len(content) > MAX_FILE_SIZE_BYTES:
        raise FileValidationError(
            f"File exceeds the {MAX_FILE_SIZE_MB} MB limit."
        )

    if Path(filename).name != filename:
        raise FileValidationError("Invalid filename.")

    try:
        file_format = detect_format(filename, content)
    except FormatDetectionError as exc:
        raise FileValidationError(str(exc)) from exc

    return {
        "filename": filename,
        "format": file_format,
        "size": len(content),
        "size_mb": round(len(content) / (1024 * 1024), 2),
        "is_valid": True,
    }
