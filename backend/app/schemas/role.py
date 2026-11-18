from pydantic import Field

from app.schemas.common import SchemaBase


class RoleCreate(SchemaBase):
    name: str = Field(min_length=2, max_length=50)
    description: str | None = None


class RoleUpdate(SchemaBase):
    name: str | None = Field(default=None, min_length=2, max_length=50)
    description: str | None = None


class RoleResponse(SchemaBase):
    id: str
    name: str
    description: str | None = None
