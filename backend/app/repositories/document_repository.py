
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_version import DocumentVersion


class DocumentRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, document_id: str):
        return (
            self.db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

    def get_by_id_and_org(
        self,
        document_id: str,
        organization_id: str,
    ):
        return (
            self.db.query(Document)
            .filter(
                Document.id == document_id,
                Document.organization_id == organization_id,
            )
            .first()
        )

    def list_by_organization(
        self,
        organization_id: str,
        skip: int = 0,
        limit: int = 50,
    ):
        return (
            self.db.query(Document)
            .filter(Document.organization_id == organization_id)
            .order_by(Document.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_by_workspace(
        self,
        workspace_id: str,
        skip: int = 0,
        limit: int = 50,
    ):
        return (
            self.db.query(Document)
            .filter(Document.workspace_id == workspace_id)
            .order_by(Document.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, document_data: dict):
        document = Document(**document_data)
        self.db.add(document)
        self.db.flush()
        return document

    def update(self, document: Document, update_data: dict):
        allowed_fields = {
            "title",
            "status",
            "current_version",
            "storage_key",
            "mime_type",
            "file_size",
        }

        for field, value in update_data.items():
            if field in allowed_fields:
                setattr(document, field, value)

        self.db.flush()
        return document

    def add_version(self, version_data: dict):
        version = DocumentVersion(**version_data)
        self.db.add(version)
        self.db.flush()
        return version

    def get_versions(self, document_id: str):
        return (
            self.db.query(DocumentVersion)
            .filter(DocumentVersion.document_id == document_id)
            .order_by(DocumentVersion.version_number.desc())
            .all()
        )

    def get_version(
        self,
        document_id: str,
        version_number: int,
    ):
        return (
            self.db.query(DocumentVersion)
            .filter(
                DocumentVersion.document_id == document_id,
                DocumentVersion.version_number == version_number,
            )
            .first()
        )

    def delete(self, document: Document):
        self.db.delete(document)
        self.db.flush()
