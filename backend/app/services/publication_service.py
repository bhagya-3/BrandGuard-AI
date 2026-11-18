
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.publication import Publication
from app.models.approval import Approval
from app.models.document import Document


class PublicationServiceError(Exception):
    pass


class PublicationService:

    def __init__(self, db: Session):
        self.db = db

    def publish_document(
        self,
        document_id: str,
        approval_id: str,
        publisher_id: str,
        external_url: str | None = None,
    ) -> Publication:

        approval = (
            self.db.query(Approval)
            .filter(
                Approval.id == approval_id,
                Approval.document_id == document_id,
            )
            .first()
        )

        if not approval:
            raise PublicationServiceError(
                "Approval record not found."
            )

        if approval.status != "approved":
            raise PublicationServiceError(
                "Document has not been approved."
            )

        if not approval.approver_id:
            raise PublicationServiceError(
                "An authorized approver is required."
            )

        document = (
            self.db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

        if not document:
            raise PublicationServiceError(
                "Document not found."
            )

        existing = (
            self.db.query(Publication)
            .filter(
                Publication.document_id == document_id,
                Publication.version_number == document.current_version,
                Publication.status == "published",
            )
            .first()
        )

        if existing:
            raise PublicationServiceError(
                "This document version is already published."
            )

        publication = Publication(
            document_id=document_id,
            approved_by=approval.approver_id,
            published_by=publisher_id,
            version_number=document.current_version,
            status="published",
            external_url=external_url,
            published_at=datetime.now(timezone.utc),
        )

        self.db.add(publication)
        self.db.flush()

        return publication

    def get_publications(self, document_id: str):
        return (
            self.db.query(Publication)
            .filter(Publication.document_id == document_id)
            .order_by(Publication.published_at.desc())
            .all()
        )
