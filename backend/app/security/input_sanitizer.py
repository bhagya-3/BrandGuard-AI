
import re
import bleach


class InputSanitizationError(Exception):
    pass


ALLOWED_TAGS = [
    "p",
    "br",
    "strong",
    "b",
    "i",
    "em",
    "u",
    "ul",
    "ol",
    "li",
    "blockquote",
]

ALLOWED_ATTRIBUTES = {}


def sanitize_html(value: str) -> str:
    if not isinstance(value, str):
        raise InputSanitizationError(
            "Input must be a string."
        )

    return bleach.clean(
        value,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True,
        strip_comments=True,
    )


def sanitize_plain_text(value: str) -> str:
    if not isinstance(value, str):
        raise InputSanitizationError(
            "Input must be a string."
        )

    # Remove null bytes and unsafe control characters.
    value = value.replace("\x00", "")

    value = re.sub(
        r"[\x01-\x08\x0B\x0C\x0E-\x1F\x7F]",
        "",
        value,
    )

    return value.strip()


def validate_text_length(
    value: str,
    minimum: int = 1,
    maximum: int = 10000,
) -> str:

    if not isinstance(value, str):
        raise InputSanitizationError(
            "Input must be a string."
        )

    value = value.strip()

    if len(value) < minimum:
        raise InputSanitizationError(
            f"Input must contain at least {minimum} characters."
        )

    if len(value) > maximum:
        raise InputSanitizationError(
            f"Input cannot exceed {maximum} characters."
        )

    return value


def sanitize_filename(filename: str) -> str:
    if not isinstance(filename, str):
        raise InputSanitizationError(
            "Filename must be a string."
        )

    filename = filename.replace("\\", "/").split("/")[-1]

    filename = re.sub(
        r"[^a-zA-Z0-9._-]",
        "_",
        filename,
    )

    filename = filename.strip("._")

    if not filename:
        raise InputSanitizationError(
            "Filename is invalid."
        )

    return filename
