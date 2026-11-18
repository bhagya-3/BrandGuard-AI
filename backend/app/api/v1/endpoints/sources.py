from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.source import Source
from app.models.source_version import SourceVersion
from app.models.user import User
from app.services.audit_service import AuditService
from app.services.source_service import SourceService, SourceServiceError


router = APIRouter()


class SourceCreate(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    source_type: str = Field(default="guideline", max_length=50)
    description: str | None = Field(default=None, max_length=2000)
    content: str = Field(min_length=1, max_length=100000)


def _source_response(source: Source) -> dict:
    return {
        "id": source.id,
        "title": source.title,
        "source_type": source.source_type,
        "description": source.description,
        "status": source.status,
        "versions": [
            {
                "id": version.id,
                "version_number": version.version_number,
                "status": version.status,
                "created_at": version.created_at,
                "approved_at": version.approved_at,
            }
            for version in sorted(source.versions, key=lambda item: item.version_number)
        ],
    }


@router.get("/")
def list_sources(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sources = (
        db.query(Source)
        .filter(Source.organization_id == user.organization_id)
        .order_by(Source.updated_at.desc())
        .all()
    )
    return [_source_response(source) for source in sources]


@router.post("/", status_code=201)
def create_source(
    payload: SourceCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = SourceService(db)
    source = service.create_source(
        organization_id=user.organization_id,
        owner_id=user.id,
        title=payload.title,
        source_type=payload.source_type,
        description=payload.description,
    )
    service.add_source_version(
        source.id,
        user.organization_id,
        payload.content,
    )
    AuditService(db).record_event(
        action="source.created",
        entity_type="source",
        entity_id=source.id,
        user_id=user.id,
        organization_id=user.organization_id,
    )
    db.commit()
    db.refresh(source)
    return _source_response(source)


@router.post("/{source_id}/versions/{version_id}/approve")
def approve_source_version(
    source_id: str,
    version_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    source = db.query(Source).filter(
        Source.id == source_id,
        Source.organization_id == user.organization_id,
    ).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found.")
    if source.owner_id == user.id:
        raise HTTPException(
            status_code=403,
            detail="A source must be verified by a different workspace member.",
        )
    try:
        service = SourceService(db)
        version = service.approve_source_version(
            source_id,
            version_id,
            user.organization_id,
            user.id,
        )
    except SourceServiceError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    AuditService(db).record_event(
        action="source.version_approved",
        entity_type="source",
        entity_id=source.id,
        user_id=user.id,
        organization_id=user.organization_id,
        details={"version_id": version.id},
    )
    db.commit()
    db.refresh(source)
    return _source_response(source)