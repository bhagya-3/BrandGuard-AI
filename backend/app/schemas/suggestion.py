
from app.schemas.common import SchemaBase, TimestampSchema


class SuggestionCreate(SchemaBase):
    finding_id: str
    original_text: str
    suggested_text: str
    rationale: str


class SuggestionUpdate(SchemaBase):
    status: str


class SuggestionResponse(TimestampSchema):
    id: str
    finding_id: str
    created_by: str | None = None
    original_text: str
    suggested_text: str
    rationale: str
    status: str
