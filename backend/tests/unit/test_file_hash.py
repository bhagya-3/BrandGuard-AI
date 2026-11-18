from app.utils.file_hash import (
    calculate_hash,
    calculate_text_hash,
    verify_hash,
)


def test_calculate_hash():
    content = b"BrandGuard AI"

    result = calculate_hash(content)

    assert isinstance(result, str)
    assert len(result) == 64


def test_same_content_produces_same_hash():
    first = calculate_hash(b"same content")
    second = calculate_hash(b"same content")

    assert first == second


def test_different_content_produces_different_hash():
    first = calculate_hash(b"first")
    second = calculate_hash(b"second")

    assert first != second


def test_calculate_text_hash():
    result = calculate_text_hash("BrandGuard AI")

    assert isinstance(result, str)
    assert len(result) == 64


def test_verify_hash():
    content = b"test content"
    expected_hash = calculate_hash(content)

    assert verify_hash(content, expected_hash)


def test_verify_wrong_hash():
    assert not verify_hash(b"test content", "incorrect-hash")