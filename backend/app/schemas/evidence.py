
from app.schemas.common import SchemaBase, TimestampSchema


class EvidenceCreate(SchemaBase):
    finding_id: str
    source_id: str | None = None
    source_version_id: str | None = None
    quote: str
    source_reference: str | None = None
    relevance_score: float | None = None


class EvidenceResponse(TimestampSchema):
    id: str
    finding_id: str
    source_id: str | None = None
    source_version_id: str | None = None
    quote: str
    source_reference: str | None = None
    relevance_score: float | None = None
