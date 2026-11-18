
import logging
from datetime import datetime, timezone
from typing import Any


logger = logging.getLogger("brandguard.security")


class SecurityEvents:

    @staticmethod
    def record(
        event_type: str,
        message: str,
        user_id: str | None = None,
        ip_address: str | None = None,
        details: dict[str, Any] | None = None,
        severity: str = "warning",
    ) -> None:

        event = {
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "event_type": event_type,
            "message": message,
            "user_id": user_id,
            "ip_address": ip_address,
            "details": details or {},
        }

        # Never include passwords, tokens, or secret values
        # in event details.

        log_message = str(event)

        if severity == "critical":
            logger.critical(log_message)

        elif severity == "error":
            logger.error(log_message)

        elif severity == "info":
            logger.info(log_message)

        else:
            logger.warning(log_message)

    @classmethod
    def failed_login(
        cls,
        email: str,
        ip_address: str | None = None,
    ) -> None:

        cls.record(
            event_type="FAILED_LOGIN",
            message="A login attempt failed.",
            ip_address=ip_address,
            details={
                "email": email,
            },
            severity="warning",
        )

    @classmethod
    def successful_login(
        cls,
        user_id: str,
        ip_address: str | None = None,
    ) -> None:

        cls.record(
            event_type="SUCCESSFUL_LOGIN",
            message="User logged in successfully.",
            user_id=user_id,
            ip_address=ip_address,
            severity="info",
        )

    @classmethod
    def blocked_upload(
        cls,
        filename: str,
        reason: str,
        user_id: str | None = None,
    ) -> None:

        cls.record(
            event_type="BLOCKED_UPLOAD",
            message="A document upload was blocked.",
            user_id=user_id,
            details={
                "filename": filename,
                "reason": reason,
            },
            severity="error",
        )

    @classmethod
    def session_revoked(
        cls,
        user_id: str,
        session_id: str,
    ) -> None:

        cls.record(
            event_type="SESSION_REVOKED",
            message="A user session was revoked.",
            user_id=user_id,
            details={
                "session_id": session_id,
            },
            severity="info",
        )

    @classmethod
    def suspicious_activity(
        cls,
        message: str,
        user_id: str | None = None,
        ip_address: str | None = None,
    ) -> None:

        cls.record(
            event_type="SUSPICIOUS_ACTIVITY",
            message=message,
            user_id=user_id,
            ip_address=ip_address,
            severity="critical",
        )


security_events = SecurityEvents()
