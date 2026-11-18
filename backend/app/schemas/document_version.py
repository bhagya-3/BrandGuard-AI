
from datetime import datetime

from app.schemas.common import SchemaBase


class DocumentVersionCreate(SchemaBase):
    document_id: str
    storage_key: str
    checksum: str
    extracted_text: str | None = None


class DocumentVersionResponse(SchemaBase):
    id: str
    document_id: str
    version_number: int
    storage_key: str
    checksum: str
    extracted_text: str | None = None
    created_by: str
    created_at: datetime
