
from datetime import datetime
from pydantic import Field

from app.schemas.common import SchemaBase, TimestampSchema


class DocumentCreate(SchemaBase):
    title: str = Field(min_length=1, max_length=250)
    workspace_id: str
    organization_id: str


class DocumentUpdate(SchemaBase):
    title: str | None = Field(default=None, min_length=1, max_length=250)
    status: str | None = None


class DocumentResponse(TimestampSchema):
    id: str
    organization_id: str
    workspace_id: str
    uploader_id: str
    title: str
    original_filename: str
    mime_type: str
    file_size: int
    status: str
    current_version: int


class DocumentVersionResponse(SchemaBase):
    id: str
    document_id: str
    version_number: int
    checksum: str
    created_by: str
    created_at: datetime


class DocumentUploadResponse(SchemaBase):
    document: DocumentResponse
    message: str
