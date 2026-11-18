
import hashlib

from sqlalchemy.orm import Session

from app.models.source import Source
from app.models.source_version import SourceVersion
from app.repositories.source_repository import SourceRepository


class SourceServiceError(Exception):
    pass


class SourceService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = SourceRepository(db)

    def create_source(
        self,
        organization_id: str,
        owner_id: str,
        title: str,
        source_type: str,
        description: str | None = None,
        workspace_id: str | None = None,
    ) -> Source:

        source = Source(
            organization_id=organization_id,
            workspace_id=workspace_id,
            owner_id=owner_id,
            title=title.strip(),
            source_type=source_type,
            description=description,
            status="pending",
        )

        self.db.add(source)
        self.db.flush()

        return source

    def add_source_version(
        self,
        source_id: str,
        organization_id: str,
        content: str,
        storage_key: str | None = None,
    ) -> SourceVersion:

        source = self.repository.get_by_id_and_org(
            source_id,
            organization_id,
        )

        if not source:
            raise SourceServiceError("Source not found.")

        if not content.strip():
            raise SourceServiceError(
                "Source content cannot be empty."
            )

        versions = self.repository.get_versions(source_id)

        version_number = (
            max((v.version_number for v in versions), default=0) + 1
        )

        checksum = hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()

        version = SourceVersion(
            source_id=source.id,
            version_number=version_number,
            storage_key=storage_key,
            content=content,
            checksum=checksum,
            status="pending",
        )

        self.db.add(version)

        # A new version must not silently inherit the previous approval.
        source.status = "pending"

        self.db.flush()
        return version

    def approve_source_version(
        self,
        source_id: str,
        version_id: str,
        organization_id: str,
        approver_id: str,
    ) -> SourceVersion:

        source = self.repository.get_by_id_and_org(
            source_id,
            organization_id,
        )

        if not source:
            raise SourceServiceError("Source not found.")

        versions = self.repository.get_versions(source_id)

        version = next(
            (v for v in versions if v.id == version_id),
            None,
        )

        if not version:
            raise SourceServiceError(
                "Source version not found."
            )

        if version.status == "approved":
            raise SourceServiceError(
                "This source version is already approved."
            )

        from datetime import datetime, timezone

        version.status = "approved"
        version.approved_by = approver_id
        version.approved_at = datetime.now(timezone.utc)

        source.status = "approved"

        self.db.flush()
        return version

    def get_approved_sources(
        self,
        organization_id: str,
    ) -> list[dict]:

        sources = self.repository.list_by_organization(
            organization_id
        )

        approved = []

        for source in sources:
            if source.status != "approved":
                continue

            versions = self.repository.get_versions(source.id)

            for version in versions:
                if (
                    version.status == "approved"
                    and version.content
                ):
                    approved.append({
                        "source_id": source.id,
                        "source_version_id": version.id,
                        "title": source.title,
                        "status": version.status,
                        "content": version.content,
                    })

        return approved
