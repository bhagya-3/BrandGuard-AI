
from datetime import datetime

from app.schemas.common import SchemaBase


class SourceVersionCreate(SchemaBase):
    source_id: str
    storage_key: str | None = None
    content: str | None = None
    checksum: str | None = None


class SourceVersionApproval(SchemaBase):
    status: str


class SourceVersionResponse(SchemaBase):
    id: str
    source_id: str
    version_number: int
    storage_key: str | None = None
    content: str | None = None
    checksum: str | None = None
    status: str
    approved_by: str | None = None
    approved_at: datetime | None = None
    created_at: datetime
