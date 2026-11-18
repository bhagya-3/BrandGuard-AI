
from datetime import datetime

from app.schemas.common import SchemaBase, TimestampSchema


class ApprovalCreate(SchemaBase):
    review_id: str
    document_id: str


class ApprovalDecision(SchemaBase):
    status: str
    decision_note: str | None = None


class ApprovalResponse(TimestampSchema):
    id: str
    review_id: str
    document_id: str
    requested_by: str
    approver_id: str | None = None
    status: str
    decision_note: str | None = None
    requested_at: datetime
    decided_at: datetime | None = None
