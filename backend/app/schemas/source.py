
from datetime import datetime
from pydantic import Field

from app.schemas.common import SchemaBase, TimestampSchema


class SourceCreate(SchemaBase):
    title: str = Field(min_length=2, max_length=250)
    source_type: str
    description: str | None = None
    organization_id: str
    workspace_id: str | None = None


class SourceUpdate(SchemaBase):
    title: str | None = Field(default=None, min_length=2, max_length=250)
    description: str | None = None
    source_type: str | None = None
    status: str | None = None


class SourceResponse(TimestampSchema):
    id: str
    organization_id: str
    workspace_id: str | None = None
    owner_id: str
    title: str
    source_type: str
    description: str | None = None
    status: str


class SourceVersionCreate(SchemaBase):
    content: str | None = None


class SourceVersionResponse(SchemaBase):
    id: str
    source_id: str
    version_number: int
    checksum: str | None = None
    status: str
    approved_by: str | None = None
    approved_at: datetime | None = None
    created_at: datetime
