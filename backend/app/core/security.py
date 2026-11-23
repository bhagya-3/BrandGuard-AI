
from datetime import datetime, timedelta, timezone
import base64
import hashlib
import hmac
import os
from typing import Any

try:
    from argon2 import PasswordHasher
    from argon2.exceptions import (
        InvalidHashError,
        VerificationError,
        VerifyMismatchError,
    )
    password_hasher = PasswordHasher()
    _HAS_ARGON2 = True
except Exception:  # pragma: no cover - fallback for locked-down environments
    password_hasher = None
    InvalidHashError = ValueError
    VerificationError = ValueError
    VerifyMismatchError = ValueError
    _HAS_ARGON2 = False

import jwt
from jwt.exceptions import InvalidTokenError

from app.core.config import settings


def _hash_password_fallback(password: str) -> str:
    salt = os.urandom(16)
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        200_000,
    )
    encoded = base64.b64encode(salt).decode("ascii")
    digest = base64.b64encode(derived).decode("ascii")
    return f"pbkdf2_sha256${encoded}${digest}"


def _verify_password_fallback(
    plain_password: str,
    hashed_password: str,
) -> bool:
    try:
        _, salt_b64, digest_b64 = hashed_password.split("$", 2)
        salt = base64.b64decode(salt_b64.encode("ascii"))
        expected = base64.b64decode(digest_b64.encode("ascii"))
        actual = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt,
            200_000,
        )
        return hmac.compare_digest(actual, expected)
    except (TypeError, ValueError):
        return False


if _HAS_ARGON2:
    def hash_password(password: str) -> str:
        if len(password) < 12:
            raise ValueError("Password must contain at least 12 characters.")

        return password_hasher.hash(password)

    def verify_password(
        plain_password: str,
        hashed_password: str,
    ) -> bool:
        try:
            return password_hasher.verify(
                hashed_password,
                plain_password,
            )
        except (
            VerifyMismatchError,
            VerificationError,
            InvalidHashError,
        ):
            return False
else:
    def hash_password(password: str) -> str:
        if len(password) < 12:
            raise ValueError("Password must contain at least 12 characters.")
        return _hash_password_fallback(password)

    def verify_password(
        plain_password: str,
        hashed_password: str,
    ) -> bool:
        return _verify_password_fallback(plain_password, hashed_password)


def create_access_token(
    subject: str,
    additional_claims: dict[str, Any] | None = None,
) -> str:
    now = datetime.now(timezone.utc)

    expires_at = now + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": subject,
        "iat": now,
        "exp": expires_at,
        "type": "access",
    }

    if additional_claims:
        reserved = {"sub", "iat", "exp", "type"}

        if reserved.intersection(additional_claims):
            raise ValueError("Additional claims contain reserved fields.")

        payload.update(additional_claims)

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

def decode_access_token(token: str) -> dict[str, Any] | None:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

        if payload.get("type") != "access":
            return None

        if not payload.get("sub"):
            return None

        return payload

    except InvalidTokenError:
        return None