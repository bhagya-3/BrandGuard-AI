
import re
from pathlib import PurePosixPath
from typing import Optional


class StorageAccessError(Exception):
    """Raised when a storage operation is not permitted."""


def validate_storage_key(storage_key: str) -> str:
    """
    Validate a storage key before using it.

    Prevents absolute paths, traversal sequences and unsafe characters.
    """
    if not storage_key or not isinstance(storage_key, str):
        raise StorageAccessError("Storage key is required.")

    key = storage_key.replace("\\", "/").strip()

    if key.startswith("/") or ".." in PurePosixPath(key).parts:
        raise StorageAccessError("Invalid storage key.")

    if re.search(r"[^a-zA-Z0-9._/-]", key):
        raise StorageAccessError("Storage key contains invalid characters.")

    if len(key) > 500:
        raise StorageAccessError("Storage key is too long.")

    return key


def build_organization_storage_key(
    organization_id: str,
    category: str,
    filename: str,
    document_id: Optional[str] = None,
) -> str:
    """Build a predictable, organization-scoped storage key."""
    if not organization_id or not category or not filename:
        raise StorageAccessError("Organization, category and filename are required.")

    safe_filename = PurePosixPath(filename.replace("\\", "/")).name
    safe_filename = re.sub(r"[^a-zA-Z0-9._-]", "_", safe_filename)

    if not safe_filename or safe_filename in {".", ".."}:
        raise StorageAccessError("Invalid filename.")

    parts = ["organizations", str(organization_id), category]

    if document_id:
        parts.append(str(document_id))

    parts.append(safe_filename)

    return validate_storage_key("/".join(parts))


def check_organization_access(
    storage_key: str,
    organization_id: str,
) -> bool:
    """
    Return True only when the key belongs to the given organization.
    """
    key = validate_storage_key(storage_key)
    expected_prefix = f"organizations/{organization_id}/"

    return key.startswith(expected_prefix)


def require_organization_access(
    storage_key: str,
    organization_id: str,
) -> None:
    """Raise an exception if the key belongs to another organization."""
    if not check_organization_access(storage_key, organization_id):
        raise StorageAccessError(
            "You do not have permission to access this file."
        )
