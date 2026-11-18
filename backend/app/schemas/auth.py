
from pydantic import EmailStr, Field

from app.schemas.common import SchemaBase


class RegisterRequest(SchemaBase):
    organization_name: str = Field(min_length=2, max_length=150)
    full_name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)


class LoginRequest(SchemaBase):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(SchemaBase):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(SchemaBase):
    refresh_token: str


class PasswordChangeRequest(SchemaBase):
    current_password: str
    new_password: str = Field(min_length=12, max_length=128)


class PasswordResetRequest(SchemaBase):
    email: EmailStr


class PasswordResetConfirm(SchemaBase):
    token: str
    new_password: str = Field(min_length=12, max_length=128)


class AuthUserResponse(SchemaBase):
    id: str
    full_name: str
    email: EmailStr
    organization_id: str | None = None
    is_active: bool
    is_verified: bool


class AuthResponse(SchemaBase):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: AuthUserResponse
