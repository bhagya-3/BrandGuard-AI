
from datetime import datetime
from pydantic import Field

from app.schemas.common import SchemaBase, TimestampSchema


class ReviewCreate(SchemaBase):
    document_id: str
    workspace_id: str
    organization_id: str


class ReviewUpdate(SchemaBase):
    status: str | None = None
    summary: str | None = None
    overall_score: float | None = Field(default=None, ge=0, le=100)


class ReviewResponse(TimestampSchema):
    id: str
    organization_id: str
    workspace_id: str
    document_id: str
    requested_by: str
    status: str
    overall_score: float | None = None
    summary: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


class ReviewRunRequest(SchemaBase):
    document_id: str
    generate_suggestions: bool = False


class ReviewSummary(SchemaBase):
    total_findings: int
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    passed: bool
