from app.utils.identifiers import (
    generate_uuid,
    generate_short_id,
    generate_token_id,
    normalize_identifier,
    is_valid_uuid,
)


def test_generate_uuid():
    value = generate_uuid()

    assert isinstance(value, str)
    assert is_valid_uuid(value)


def test_generate_short_id():
    value = generate_short_id()

    assert isinstance(value, str)
    assert len(value) > 0


def test_generate_token_id():
    value = generate_token_id()

    assert isinstance(value, str)
    assert value.startswith("BG-")


def test_normalize_identifier():
    assert normalize_identifier("  BrandGuard AI  ") == "brandguard-ai"


def test_invalid_uuid():
    assert not is_valid_uuid("not-a-valid-uuid")