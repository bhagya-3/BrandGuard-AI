
from datetime import datetime

from app.schemas.common import SchemaBase, TimestampSchema


class PublicationCreate(SchemaBase):
    document_id: str
    version_number: int


class PublicationUpdate(SchemaBase):
    status: str | None = None
    external_url: str | None = None


class PublicationResponse(TimestampSchema):
    id: str
    document_id: str
    approved_by: str
    published_by: str | None = None
    version_number: int
    status: str
    external_url: str | None = None
    published_at: datetime | None = None
