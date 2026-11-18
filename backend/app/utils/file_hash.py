
import hashlib
import hmac
from pathlib import Path
from typing import Union


class FileHashError(Exception):
    """Raised when a file cannot be hashed."""


def calculate_bytes_hash(content: bytes) -> str:
    """Calculate SHA-256 hash from file bytes."""
    if not isinstance(content, bytes):
        raise FileHashError("Content must be bytes.")

    return hashlib.sha256(content).hexdigest()


def calculate_file_hash(
    file_path: Union[str, Path],
    chunk_size: int = 1024 * 1024,
) -> str:
    """Calculate SHA-256 hash without loading the entire file into memory."""
    path = Path(file_path)

    if not path.exists():
        raise FileHashError("File does not exist.")

    if not path.is_file():
        raise FileHashError("Path is not a file.")

    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero.")

    sha256 = hashlib.sha256()

    try:
        with path.open("rb") as file:
            while True:
                chunk = file.read(chunk_size)

                if not chunk:
                    break

                sha256.update(chunk)

        return sha256.hexdigest()

    except OSError as exc:
        raise FileHashError("Unable to read file for hashing.") from exc


def verify_bytes_hash(
    content: bytes,
    expected_hash: str,
) -> bool:
    """Verify bytes against an expected SHA-256 hash."""
    if not expected_hash:
        return False

    actual_hash = calculate_bytes_hash(content)

    return hmac.compare_digest(
        actual_hash,
        expected_hash.lower(),
    )


def verify_file_hash(
    file_path: Union[str, Path],
    expected_hash: str,
) -> bool:
    """Verify a file against an expected SHA-256 hash."""
    if not expected_hash:
        return False

    actual_hash = calculate_file_hash(file_path)

    return hmac.compare_digest(
        actual_hash,
        expected_hash.lower(),
    )


def calculate_text_hash(text: str) -> str:
    """Calculate SHA-256 hash from text."""
    if not isinstance(text, str):
        raise FileHashError("Text must be a string.")

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


calculate_hash = calculate_bytes_hash
verify_hash = verify_bytes_hash
