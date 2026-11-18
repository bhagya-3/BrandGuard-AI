
from pathlib import Path
from zipfile import BadZipFile, ZipFile
from io import BytesIO


class FormatDetectionError(ValueError):
    pass


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".pptx",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".txt",
}


def detect_format(filename: str, content: bytes) -> str:
    if not content:
        raise FormatDetectionError("Uploaded file is empty.")

    extension = Path(filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise FormatDetectionError(
            f"Unsupported file extension: {extension}"
        )

    if content.startswith(b"%PDF-"):
        detected = "pdf"

    elif content.startswith(b"\x89PNG\r\n\x1a\n"):
        detected = "png"

    elif content.startswith(b"\xff\xd8\xff"):
        detected = "jpeg"

    elif content.startswith(b"RIFF") and content[8:12] == b"WEBP":
        detected = "webp"

    elif content.startswith(b"PK"):
        try:
            with ZipFile(BytesIO(content)) as archive:
                names = set(archive.namelist())

                if "word/document.xml" in names:
                    detected = "docx"
                elif "ppt/presentation.xml" in names:
                    detected = "pptx"
                else:
                    raise FormatDetectionError(
                        "ZIP file is not a supported DOCX or PPTX."
                    )
        except BadZipFile as exc:
            raise FormatDetectionError(
                "Invalid Office document archive."
            ) from exc

    elif extension == ".txt":
        try:
            content.decode("utf-8")
            detected = "txt"
        except UnicodeDecodeError as exc:
            raise FormatDetectionError(
                "Text file must use UTF-8 encoding."
            ) from exc

    else:
        raise FormatDetectionError(
            "File content does not match a supported format."
        )

    expected_extension = {
        "pdf": ".pdf",
        "png": ".png",
        "jpeg": ".jpg",
        "webp": ".webp",
        "docx": ".docx",
        "pptx": ".pptx",
        "txt": ".txt",
    }[detected]

    compatible_extensions = {
        "jpeg": {".jpg", ".jpeg"},
    }

    allowed = compatible_extensions.get(
        detected, {expected_extension}
    )

    if extension not in allowed:
        raise FormatDetectionError(
            "File extension does not match its actual content."
        )

    return detected
