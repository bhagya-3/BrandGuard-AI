
import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.core.config import settings
from app.models.document import Document
from app.models.document_version import DocumentVersion
from app.models.outbox_event import OutboxEvent
from app.models.review import Review
from app.models.user import User
from app.models.workspace import Workspace
from app.services.document_service import DocumentService, DocumentServiceError
from app.storage.factory import get_storage


router = APIRouter()
logger = logging.getLogger(__name__)


def _document_response(document: Document, db: Session) -> dict:
    latest = (
        db.query(Review)
        .filter(Review.document_id == document.id)
        .order_by(Review.created_at.desc())
        .first()
    )

    findings = latest.findings if latest else []

    return {
        "id": document.id,
        "organization_id": document.organization_id,
        "workspace_id": document.workspace_id,
        "uploaded_by": document.uploaded_by,
        "title": document.title,
        "original_filename": document.original_filename,
        "mime_type": document.mime_type,
        "file_size": document.file_size,
        "status": document.status,
        "current_version": document.current_version,
        "created_at": document.created_at,
        "updated_at": document.updated_at,
        "latest_review_id": latest.id if latest else None,
        "latest_review_status": latest.status if latest else None,
        "finding_count": len(findings),
    }


@router.get("/")
def list_documents(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    documents = DocumentService(db).list_documents(
        user.organization_id
    )

    return [
        _document_response(item, db)
        for item in documents
    ]


@router.post("/upload", status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    workspace_id: str | None = Form(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not user.organization_id:
        raise HTTPException(
            status_code=403,
            detail="Account has no organization.",
        )

    workspace = db.query(Workspace).filter(
        Workspace.organization_id == user.organization_id,
        Workspace.id == workspace_id if workspace_id else True,
    ).first()

    if not workspace:
        raise HTTPException(
            status_code=404,
            detail="Workspace not found.",
        )

    content = await file.read(
        settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024 + 1
    )

    if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=(
                f"File exceeds the {settings.MAX_UPLOAD_SIZE_MB} "
                "MB upload limit."
            ),
        )

    try:
        document = DocumentService(
            db,
            storage=get_storage(),
        ).upload_document(
            filename=file.filename or "",
            content=content,
            organization_id=user.organization_id,
            workspace_id=workspace.id,
            uploader_id=user.id,
        )

        # Ensure the document and its version have database IDs.
        db.flush()

        # Record the processing request in the same transaction.
        outbox_event = OutboxEvent(
            event_type="document.process",
            aggregate_type="document",
            aggregate_id=document.id,
            payload={
                "document_id": document.id,
                "organization_id": user.organization_id,
            },
            status="pending",
            attempts=0,
        )

        db.add(outbox_event)

        # Document, version and outbox event commit together.
        db.commit()
        db.refresh(document)

        logger.info(
            "Document and outbox event saved. Document: %s, Event: %s",
            document.id,
            outbox_event.id,
        )

    except DocumentServiceError as exc:
        db.rollback()
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        db.rollback()
        logger.exception("Document upload transaction failed.")

        raise HTTPException(
            status_code=500,
            detail="Unable to save the document. Please try again.",
        ) from exc

    return _document_response(document, db)


@router.get("/{document_id}")
def get_document(
    document_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        document = DocumentService(db).get_document(
            document_id,
            user.organization_id,
        )

    except DocumentServiceError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return _document_response(document, db)
