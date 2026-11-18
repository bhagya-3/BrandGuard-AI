
from pydantic import Field

from app.schemas.common import SchemaBase, TimestampSchema


class FindingCreate(SchemaBase):
    review_id: str
    document_id: str
    category: str
    severity: str
    title: str
    description: str
    location: str | None = None


class FindingUpdate(SchemaBase):
    status: str | None = None
    severity: str | None = None
    description: str | None = None


class FindingResponse(TimestampSchema):
    id: str
    review_id: str
    document_id: str
    category: str
    severity: str
    title: str
    description: str
    location: str | None = None
    status: str


class FindingListResponse(SchemaBase):
    findings: list[FindingResponse]
    total: int
