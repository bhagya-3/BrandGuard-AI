
import hashlib

from datetime import datetime, timezone, timedelta
from typing import Any

try:
    from sqlalchemy.orm import Session as DBSession
except Exception:  # pragma: no cover - optional dependency fallback
    DBSession = Any

try:
    from app.models.session import Session
except Exception:  # pragma: no cover - DB model imports are optional in restricted environments
    class Session:  # type: ignore[no-redef]
        pass


class SessionSecurityError(Exception):
    pass


def hash_session_token(token: str) -> str:
    if not token:
        raise SessionSecurityError(
            "Session token cannot be empty."
        )

    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


class SessionManager:

    @staticmethod
    def create_session(
        db: DBSession,
        user_id: str,
        token: str,
        expires_in_minutes: int = 60,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> Session:

        if expires_in_minutes <= 0:
            raise SessionSecurityError(
                "Session expiry must be positive."
            )

        session = Session(
            user_id=user_id,
            token_hash=hash_session_token(token),
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=datetime.now(timezone.utc)
            + timedelta(minutes=expires_in_minutes),
            is_active=True,
        )

        db.add(session)
        db.flush()

        return session

    @staticmethod
    def get_valid_session(
        db: DBSession,
        token: str,
    ) -> Session | None:

        token_hash = hash_session_token(token)

        session = (
            db.query(Session)
            .filter(
                Session.token_hash == token_hash,
                Session.is_active.is_(True),
                Session.revoked_at.is_(None),
            )
            .first()
        )

        if not session:
            return None

        now = datetime.now(timezone.utc)
        expires_at = session.expires_at

        # Support databases that return naive UTC datetimes.
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(
                tzinfo=timezone.utc
            )

        if expires_at <= now:
            session.is_active = False
            db.flush()
            return None

        return session

    @staticmethod
    def revoke_session(
        db: DBSession,
        session_id: str,
        user_id: str | None = None,
    ) -> bool:

        query = db.query(Session).filter(
            Session.id == session_id,
            Session.is_active.is_(True),
        )

        if user_id:
            query = query.filter(
                Session.user_id == user_id
            )

        session = query.first()

        if not session:
            return False

        session.is_active = False
        session.revoked_at = datetime.now(timezone.utc)

        db.flush()
        return True

    @staticmethod
    def revoke_all_user_sessions(
        db: DBSession,
        user_id: str,
    ) -> int:

        sessions = (
            db.query(Session)
            .filter(
                Session.user_id == user_id,
                Session.is_active.is_(True),
            )
            .all()
        )

        now = datetime.now(timezone.utc)

        for session in sessions:
            session.is_active = False
            session.revoked_at = now

        db.flush()

        return len(sessions)


session_manager = SessionManager()
