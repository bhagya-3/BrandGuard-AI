
import hashlib

from sqlalchemy.orm import Session

from app.models.document_version import DocumentVersion
from app.repositories.document_repository import DocumentRepository


class VersionServiceError(Exception):
    pass


class VersionService:

    def __init__(self, db: Session):
        self.db = db
        self.documents = DocumentRepository(db)

    def create_version(
        self,
        document_id: str,
        organization_id: str,
        storage_key: str,
        content: bytes,
        created_by: str,
    ) -> DocumentVersion:

        document = self.documents.get_by_id_and_org(
            document_id,
            organization_id,
        )

        if not document:
            raise VersionServiceError("Document not found.")

        checksum = hashlib.sha256(content).hexdigest()

        existing_versions = self.documents.get_versions(
            document_id
        )

        for version in existing_versions:
            if version.checksum == checksum:
                raise VersionServiceError(
                    "This content already exists as a document version."
                )

        version_number = document.current_version + 1

        version = DocumentVersion(
            document_id=document.id,
            version_number=version_number,
            storage_key=storage_key,
            checksum=checksum,
            created_by=created_by,
        )

        self.db.add(version)

        document.current_version = version_number
        self.db.flush()

        return version

    def get_versions(
        self,
        document_id: str,
        organization_id: str,
    ):
        document = self.documents.get_by_id_and_org(
            document_id,
            organization_id,
        )

        if not document:
            raise VersionServiceError("Document not found.")

        return self.documents.get_versions(document_id)

    def get_version(
        self,
        document_id: str,
        version_number: int,
        organization_id: str,
    ):
        document = self.documents.get_by_id_and_org(
            document_id,
            organization_id,
        )

        if not document:
            raise VersionServiceError("Document not found.")

        versions = self.documents.get_versions(document_id)

        for version in versions:
            if version.version_number == version_number:
                return version

        raise VersionServiceError("Document version not found.")
