from pydantic import Field

from app.schemas.common import SchemaBase


class PermissionCreate(SchemaBase):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = None


class PermissionResponse(SchemaBase):
    id: str
    name: str
    description: str | None = None


class RolePermissionUpdate(SchemaBase):
    permission_ids: list[str] = Field(default_factory=list)
