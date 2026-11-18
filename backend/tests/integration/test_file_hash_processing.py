from app.utils.file_hash import calculate_hash, verify_hash


def test_document_integrity_check():
    original_file = b"Original BrandGuard document"

    stored_hash = calculate_hash(original_file)

    assert verify_hash(original_file, stored_hash)


def test_modified_document_fails_integrity_check():
    original_file = b"Original BrandGuard document"
    modified_file = b"Modified BrandGuard document"

    stored_hash = calculate_hash(original_file)

    assert not verify_hash(modified_file, stored_hash)