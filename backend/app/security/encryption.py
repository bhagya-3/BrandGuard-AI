
import os
from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken


class EncryptionError(Exception):
    pass


@lru_cache(maxsize=1)
def get_fernet() -> Fernet:
    key = os.getenv("DATA_ENCRYPTION_KEY")

    if not key:
        raise EncryptionError(
            "DATA_ENCRYPTION_KEY is not configured."
        )

    try:
        return Fernet(key.encode("utf-8"))
    except Exception as exc:
        raise EncryptionError(
            "DATA_ENCRYPTION_KEY is invalid."
        ) from exc


def encrypt_data(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("Value to encrypt must be a string.")

    encrypted = get_fernet().encrypt(value.encode("utf-8"))
    return encrypted.decode("utf-8")


def decrypt_data(encrypted_value: str) -> str:
    try:
        decrypted = get_fernet().decrypt(
            encrypted_value.encode("utf-8")
        )
        return decrypted.decode("utf-8")

    except InvalidToken as exc:
        raise EncryptionError(
            "Unable to decrypt data: invalid token or key."
        ) from exc

    except Exception as exc:
        raise EncryptionError(
            "Unable to decrypt the supplied data."
        ) from exc


def generate_encryption_key() -> str:
    return Fernet.generate_key().decode("utf-8")
