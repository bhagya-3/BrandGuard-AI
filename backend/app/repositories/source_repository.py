
from sqlalchemy.orm import Session

from app.models.source import Source
from app.models.source_version import SourceVersion


class SourceRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, source_id: str):
        return (
            self.db.query(Source)
            .filter(Source.id == source_id)
            .first()
        )

    def get_by_id_and_org(
        self,
        source_id: str,
        organization_id: str,
    ):
        return (
            self.db.query(Source)
            .filter(
                Source.id == source_id,
                Source.organization_id == organization_id,
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
            self.db.query(Source)
            .filter(Source.organization_id == organization_id)
            .order_by(Source.created_at.desc())
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
            self.db.query(Source)
            .filter(Source.workspace_id == workspace_id)
            .order_by(Source.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, source_data: dict):
        source = Source(**source_data)
        self.db.add(source)
        self.db.flush()
        return source

    def update(self, source: Source, update_data: dict):
        allowed_fields = {
            "title",
            "description",
            "source_type",
            "status",
            "workspace_id",
        }

        for field, value in update_data.items():
            if field in allowed_fields:
                setattr(source, field, value)

        self.db.flush()
        return source

    def add_version(self, version_data: dict):
        version = SourceVersion(**version_data)
        self.db.add(version)
        self.db.flush()
        return version

    def get_versions(self, source_id: str):
        return (
            self.db.query(SourceVersion)
            .filter(SourceVersion.source_id == source_id)
            .order_by(SourceVersion.version_number.desc())
            .all()
        )

    def get_latest_version(self, source_id: str):
        return (
            self.db.query(SourceVersion)
            .filter(SourceVersion.source_id == source_id)
            .order_by(SourceVersion.version_number.desc())
            .first()
        )

    def delete(self, source: Source):
        self.db.delete(source)
        self.db.flush()
