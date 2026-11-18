
import os
import re
from pathlib import Path

from app.processors.file_validator import (
    validate_file,
    FileValidationError,
)


class FileSecurityError(Exception):
    pass


MAX_UPLOAD_SIZE = 25 * 1024 * 1024

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".pptx",
    ".txt",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
}


def sanitize_filename(filename: str) -> str:
    if not filename or not filename.strip():
        raise FileSecurityError("Filename cannot be empty.")

    filename = filename.replace("\\", "/")
    filename = filename.split("/")[-1]

    filename = re.sub(
        r"[^a-zA-Z0-9._-]",
        "_",
        filename,
    )

    filename = filename.strip("._")

    if not filename:
        raise FileSecurityError("Invalid filename.")

    if len(filename) > 180:
        raise FileSecurityError("Filename is too long.")

    return filename


def validate_upload(
    filename: str,
    content: bytes,
) -> dict:

    if not isinstance(content, bytes) or not content:
        raise FileSecurityError("Uploaded file is empty or invalid.")

    if len(content) > MAX_UPLOAD_SIZE:
        raise FileSecurityError("File exceeds the 25 MB limit.")

    safe_name = sanitize_filename(filename)

    extension = Path(safe_name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise FileSecurityError(
            f"File extension {extension} is not allowed."
        )

    try:
        processor_result = validate_file(
            safe_name,
            content,
        )

    except FileValidationError as exc:
        raise FileSecurityError(str(exc)) from exc

    except Exception as exc:
        raise FileSecurityError(
            "File validation failed."
        ) from exc

    return {
        "filename": safe_name,
        "extension": extension,
        "size": len(content),
        "validated": True,
        "processor_result": processor_result,
    }


def validate_storage_key(storage_key: str) -> str:
    if not storage_key:
        raise FileSecurityError("Storage key is required.")

    normalized = storage_key.replace("\\", "/")

    if normalized.startswith("/") or ".." in normalized.split("/"):
        raise FileSecurityError("Unsafe storage key.")

    if "\x00" in normalized:
        raise FileSecurityError("Invalid storage key.")

    return normalized
