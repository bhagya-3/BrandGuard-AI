from pydantic import Field

from app.schemas.common import SchemaBase, TimestampSchema


class WorkspaceCreate(SchemaBase):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None


class WorkspaceUpdate(SchemaBase):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None


class WorkspaceResponse(TimestampSchema):
    id: str
    organization_id: str
    name: str
    description: str | None = None
    created_by: str
