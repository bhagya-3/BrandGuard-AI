import pytest

from app.security.file_security import (
    sanitize_filename,
    validate_storage_key,
)


def test_sanitize_filename():
    result = sanitize_filename("../../my document.pdf")

    assert ".." not in result
    assert "/" not in result
    assert "\\" not in result


def test_valid_storage_key():
    result = validate_storage_key("organization-1/documents/report.pdf")

    assert result is not None


@pytest.mark.parametrize(
    "storage_key",
    [
        "../secret.txt",
        "../../private/file.pdf",
        "/etc/passwd",
        "folder/../../secret.txt",
    ],
)
def test_invalid_storage_keys(storage_key):
    with pytest.raises((ValueError, Exception)):
        validate_storage_key(storage_key)