
from pydantic import Field

from app.schemas.common import SchemaBase, TimestampSchema


class OrganizationCreate(SchemaBase):
    name: str = Field(min_length=2, max_length=150)
    slug: str = Field(min_length=2, max_length=100)


class OrganizationUpdate(SchemaBase):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    slug: str | None = Field(default=None, min_length=2, max_length=100)
    is_active: bool | None = None


class OrganizationResponse(TimestampSchema):
    id: str
    name: str
    slug: str
    is_active: bool
