
from app.schemas.common import SchemaBase, TimestampSchema


class BrandValueCreate(SchemaBase):
    name: str
    category: str
    value: str
    description: str | None = None
    source_id: str | None = None


class BrandValueUpdate(SchemaBase):
    name: str | None = None
    category: str | None = None
    value: str | None = None
    description: str | None = None
    status: str | None = None


class BrandValueResponse(TimestampSchema):
    id: str
    organization_id: str
    source_id: str | None = None
    name: str
    category: str
    value: str
    description: str | None = None
    status: str
    approved_by: str | None = None
