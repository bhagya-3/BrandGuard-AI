from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.approval import Approval
from app.models.document import Document
from app.models.finding import Finding
from app.models.review import Review
from app.models.user import User
from app.services.approval_service import ApprovalService, ApprovalServiceError
from app.services.audit_service import AuditService


router = APIRouter()


class ApprovalCreate(BaseModel):
    review_id: str


class ApprovalDecision(BaseModel):
    decision: str = Field(pattern="^(approved|rejected)$")
    decision_note: str | None = Field(default=None, max_length=2000)


def _approval_response(approval: Approval) -> dict:
    return {
        "id": approval.id,
        "review_id": approval.review_id,
        "document_id": approval.document_id,
        "status": approval.status,
        "decision_note": approval.decision_note,
        "requested_at": approval.requested_at,
        "decided_at": approval.decided_at,
        "document_title": approval.document.title,
        "requester": approval.requester.full_name,
    }


@router.get("/")
def list_approvals(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    approvals = (
        db.query(Approval)
        .join(Review, Approval.review_id == Review.id)
        .filter(Review.organization_id == user.organization_id)
        .order_by(Approval.requested_at.desc())
        .all()
    )
    return [_approval_response(approval) for approval in approvals]


@router.post("/", status_code=201)
def request_approval(
    payload: ApprovalCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    review = db.query(Review).filter(
        Review.id == payload.review_id,
        Review.organization_id == user.organization_id,
    ).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found.")
    unresolved = db.query(Finding).filter(
        Finding.review_id == review.id,
        Finding.status == "open",
    ).count()
    if unresolved:
        raise HTTPException(
            status_code=409,
            detail="Resolve or dismiss every finding before requesting approval.",
        )
    try:
        approval = ApprovalService(db).request_approval(
            review.id,
            review.document_id,
            user.id,
            user.organization_id,
        )
    except ApprovalServiceError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    AuditService(db).record_event(
        action="approval.requested",
        entity_type="approval",
        entity_id=approval.id,
        user_id=user.id,
        organization_id=user.organization_id,
        details={"review_id": review.id},
    )
    db.commit()
    db.refresh(approval)
    return _approval_response(approval)


@router.patch("/{approval_id}/decision")
def decide_approval(
    approval_id: str,
    payload: ApprovalDecision,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    approval = (
        db.query(Approval)
        .join(Review, Approval.review_id == Review.id)
        .filter(
            Approval.id == approval_id,
            Review.organization_id == user.organization_id,
        )
        .first()
    )
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found.")
    try:
        approval = ApprovalService(db).decide(
            approval.id,
            user.id,
            payload.decision,
            payload.decision_note,
        )
    except ApprovalServiceError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    document = db.query(Document).filter(
        Document.id == approval.document_id
    ).first()
    if document:
        document.status = (
            "approved" if payload.decision == "approved" else "changes_requested"
        )
    approval.decided_at = datetime.now(timezone.utc)
    AuditService(db).record_event(
        action=f"approval.{payload.decision}",
        entity_type="approval",
        entity_id=approval.id,
        user_id=user.id,
        organization_id=user.organization_id,
        details={"review_id": approval.review_id, "decision_note": payload.decision_note},
    )
    db.commit()
    db.refresh(approval)
    return _approval_response(approval)