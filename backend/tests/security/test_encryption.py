import os

from cryptography.fernet import Fernet

# Set a temporary test key before importing encryption functions.
os.environ["DATA_ENCRYPTION_KEY"] = Fernet.generate_key().decode()

from app.security.encryption import (
    encrypt_data,
    decrypt_data,
)


def test_encrypt_data():
    encrypted = encrypt_data("BrandGuard confidential data")

    assert encrypted != "BrandGuard confidential data"


def test_decrypt_data():
    original = "BrandGuard confidential data"

    encrypted = encrypt_data(original)
    decrypted = decrypt_data(encrypted)

    assert decrypted == original


def test_encryption_changes_plain_text():
    original = "Sensitive information"

    encrypted = encrypt_data(original)

    assert original not in encrypted