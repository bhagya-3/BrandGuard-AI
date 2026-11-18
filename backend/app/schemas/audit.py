
from datetime import datetime
from typing import Any

from app.schemas.common import SchemaBase


class AuditLogCreate(SchemaBase):
    organization_id: str | None = None
    user_id: str | None = None
    action: str
    entity_type: str
    entity_id: str | None = None
    details: dict[str, Any] | None = None
    ip_address: str | None = None


class AuditLogResponse(SchemaBase):
    id: str
    organization_id: str | None = None
    user_id: str | None = None
    action: str
    entity_type: str
    entity_id: str | None = None
    details: dict[str, Any] | None = None
    ip_address: str | None = None
    created_at: datetime
