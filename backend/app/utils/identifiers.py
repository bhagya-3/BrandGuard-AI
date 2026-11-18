
import re
import uuid
from typing import Optional


def generate_uuid() -> str:
    """Generate a unique UUID string."""
    return str(uuid.uuid4())


def generate_short_id(length: int = 12) -> str:
    """Generate a short hexadecimal identifier."""
    if length < 4 or length > 32:
        raise ValueError("Length must be between 4 and 32.")

    return uuid.uuid4().hex[:length]


def generate_token_id(prefix: str = "BG") -> str:
    """Generate a readable BrandGuard reference ID."""
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,10}", prefix):
        raise ValueError("Invalid identifier prefix.")

    unique_part = uuid.uuid4().hex[:12].upper()

    return f"{prefix.upper()}-{unique_part}"


def is_valid_uuid(value: Optional[str]) -> bool:
    """Check whether a value is a valid UUID."""
    if not isinstance(value, str):
        return False

    try:
        uuid.UUID(value)
        return True
    except (ValueError, TypeError, AttributeError):
        return False


def normalize_identifier(value: str) -> str:
    """Normalize an identifier for consistent storage and retrieval."""
    if not isinstance(value, str):
        raise ValueError("Identifier must be a string.")

    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    normalized = normalized.strip("-")

    if not normalized:
        raise ValueError("Identifier cannot be empty.")

    if len(normalized) > 128:
        raise ValueError("Identifier is too long.")

    return normalized


def validate_reference_id(
    value: str,
    prefix: Optional[str] = None,
) -> bool:
    """Validate a generated reference ID."""
    if not isinstance(value, str):
        return False

    pattern = r"[A-Z0-9_-]{1,10}-[A-F0-9]{12}"

    if not re.fullmatch(pattern, value):
        return False

    if prefix and not value.startswith(prefix.upper() + "-"):
        return False

    return True
