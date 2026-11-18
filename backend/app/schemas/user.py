
from pydantic import EmailStr, Field

from app.schemas.common import SchemaBase, TimestampSchema


class UserCreate(SchemaBase):
    full_name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    organization_id: str


class UserUpdate(SchemaBase):
    full_name: str | None = Field(default=None, min_length=2, max_length=150)
    email: EmailStr | None = None
    is_active: bool | None = None
    is_verified: bool | None = None


class UserResponse(TimestampSchema):
    id: str
    full_name: str
    email: EmailStr
    organization_id: str | None = None
    is_active: bool
    is_verified: bool


class UserListResponse(SchemaBase):
    users: list[UserResponse]
    total: int


class UserRoleUpdate(SchemaBase):
    role_ids: list[str] = Field(default_factory=list)
