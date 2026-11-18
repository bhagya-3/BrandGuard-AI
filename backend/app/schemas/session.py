
from datetime import datetime

from app.schemas.common import SchemaBase


class SessionCreate(SchemaBase):
    user_id: str
    token_hash: str
    ip_address: str | None = None
    user_agent: str | None = None
    expires_at: datetime


class SessionResponse(SchemaBase):
    id: str
    user_id: str
    ip_address: str | None = None
    user_agent: str | None = None
    expires_at: datetime
    revoked_at: datetime | None = None
    is_active: bool
    created_at: datetime


class SessionRevokeRequest(SchemaBase):
    session_id: str
