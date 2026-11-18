
from typing import Any

from pydantic import Field

from app.schemas.common import SchemaBase, TimestampSchema


class BrandRuleCreate(SchemaBase):
    name: str = Field(min_length=2, max_length=200)
    description: str | None = None
    source_id: str | None = None
    brand_value_id: str | None = None
    rule_type: str
    match_type: str = "exact"
    rule_config: dict[str, Any] = Field(default_factory=dict)
    severity: str = "medium"
    is_active: bool = True


class BrandRuleUpdate(SchemaBase):
    name: str | None = None
    description: str | None = None
    source_id: str | None = None
    brand_value_id: str | None = None
    rule_type: str | None = None
    match_type: str | None = None
    rule_config: dict[str, Any] | None = None
    severity: str | None = None
    is_active: bool | None = None


class BrandRuleResponse(TimestampSchema):
    id: str
    organization_id: str
    source_id: str | None = None
    brand_value_id: str | None = None
    created_by: str
    name: str
    description: str | None = None
    rule_type: str
    match_type: str
    rule_config: dict[str, Any]
    severity: str
    is_active: bool
