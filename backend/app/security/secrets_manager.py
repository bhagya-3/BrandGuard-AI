
import os
import logging

logger = logging.getLogger(__name__)


class SecretManagerError(Exception):
    pass


class SecretsManager:

    REQUIRED_SECRETS = [
        "JWT_SECRET_KEY",
        "DATA_ENCRYPTION_KEY",
    ]

    @staticmethod
    def get_secret(
        name: str,
        required: bool = True,
    ) -> str | None:

        value = os.getenv(name)

        if value:
            return value

        if required:
            raise SecretManagerError(
                f"Required secret '{name}' is not configured."
            )

        return None

    @staticmethod
    def validate_required_secrets() -> None:

        missing = []

        for name in SecretsManager.REQUIRED_SECRETS:
            value = os.getenv(name)

            if not value:
                missing.append(name)

        if missing:
            raise SecretManagerError(
                "Missing required secrets: "
                + ", ".join(missing)
            )

        jwt_secret = os.getenv("JWT_SECRET_KEY", "")

        if len(jwt_secret) < 32:
            raise SecretManagerError(
                "JWT_SECRET_KEY must contain at least 32 characters."
            )

    @staticmethod
    def get_optional_secret(name: str) -> str | None:
        return SecretsManager.get_secret(
            name,
            required=False,
        )

    @staticmethod
    def mask_secret(value: str | None) -> str:
        if not value:
            return "NOT_CONFIGURED"

        if len(value) <= 8:
            return "********"

        return value[:4] + "********" + value[-4:]


secrets_manager = SecretsManager()
