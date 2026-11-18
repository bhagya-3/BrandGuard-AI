
from app.schemas.common import SchemaBase, TimestampSchema


class CommentCreate(SchemaBase):
    body: str
    document_id: str | None = None
    review_id: str | None = None
    finding_id: str | None = None
    parent_comment_id: str | None = None


class CommentUpdate(SchemaBase):
    body: str


class CommentResponse(TimestampSchema):
    id: str
    document_id: str | None = None
    review_id: str | None = None
    finding_id: str | None = None
    user_id: str
    parent_comment_id: str | None = None
    body: str
