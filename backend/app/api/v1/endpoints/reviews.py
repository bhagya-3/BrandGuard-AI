from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.core.config import settings
from app.models.document import Document
from app.models.finding import Finding
from app.models.review import Review
from app.models.user import User
from app.processors.text_extractor import TextExtractionError, extract_text
from app.services.audit_service import AuditService
from app.services.review_service import ReviewService, ReviewServiceError
from app.storage.factory import get_storage


router = APIRouter()


def _review_response(review: Review) -> dict:
    return {
        "id": review.id,
        "document_id": review.document_id,
        "status": review.status,
        "summary": review.summary,
        "overall_score": review.overall_score,
        "created_at": review.created_at,
        "completed_at": review.completed_at,
        "findings": [
            {
                "id": finding.id,
                "category": finding.category,
                "severity": finding.severity,
                "title": finding.title,
                "description": finding.description,
                "location": finding.location,
                "status": finding.status,
                "evidence": [
                    {
                        "quote": evidence.quote,
                        "source_id": evidence.source_id,
                        "source_version_id": evidence.source_version_id,
                        "source_reference": evidence.source_reference,
                        "relevance_score": evidence.relevance_score,
                    }
                    for evidence in finding.evidence_items
                ],
                "suggestions": [
                    {
                        "id": suggestion.id,
                        "original_text": suggestion.original_text,
                        "suggested_text": suggestion.suggested_text,
                        "rationale": suggestion.rationale,
                        "status": suggestion.status,
                    }
                    for suggestion in finding.suggestions
                ],
            }
            for finding in review.findings
        ],
    }


@router.post("/{document_id}/run", status_code=201)
def run_review(
    document_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.organization_id == user.organization_id,
    ).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")

    try:
        content = get_storage().download_file(document.storage_key)
        extracted = extract_text(document.original_filename, content)
        if not extracted["text"].strip():
            raise HTTPException(
                status_code=422,
                detail="No readable text was found in this file.",
            )
        review = ReviewService(db).run_review(
            document_id=document.id,
            organization_id=document.organization_id,
            workspace_id=document.workspace_id,
            requested_by=user.id,
            extracted_text=extracted["text"],
            generate_suggestions=bool(settings.LLM_API_KEY.strip()),
        )
        document.status = "in_review"
        AuditService(db).record_event(
            action="review.completed",
            entity_type="review",
            entity_id=review.id,
            user_id=user.id,
            organization_id=user.organization_id,
            details={"document_id": document.id, "finding_count": len(review.findings)},
        )
        db.commit()
        db.refresh(review)
        return _review_response(review)
    except TextExtractionError as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ReviewServiceError as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{review_id}")
def get_review(
    review_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        review = ReviewService(db).get_review(review_id, user.organization_id)
    except ReviewServiceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _review_response(review)


@router.get("/")
def list_reviews(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reviews = ReviewService(db).list_reviews(user.organization_id)
    return [_review_response(review) for review in reviews]