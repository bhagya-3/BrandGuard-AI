
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.finding import Finding
from app.models.review import Review
from app.models.suggestion import Suggestion
from app.models.user import User
from app.services.audit_service import AuditService


router = APIRouter()


class FindingDecision(BaseModel):
    decision: str = Field(
        pattern="^(resolved|dismissed|open|accepted|rejected|edited)$"
    )


class SuggestionDecision(BaseModel):
    decision: Literal["accepted", "rejected", "edited"]
    suggested_text: str | None = Field(
        default=None,
        max_length=50000,
    )


def get_finding_for_user(
    finding_id: str,
    user: User,
    db: Session,
):
    finding = (
        db.query(Finding)
        .join(Review, Finding.review_id == Review.id)
        .filter(
            Finding.id == finding_id,
            Review.organization_id == user.organization_id,
        )
        .first()
    )

    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found.")

    return finding


@router.patch("/{finding_id}/decision")
def decide_finding(
    finding_id: str,
    payload: FindingDecision,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    finding = get_finding_for_user(finding_id, user, db)

    decision_map = {
        "accepted": "resolved",
        "edited": "resolved",
        "rejected": "dismissed",
        "resolved": "resolved",
        "dismissed": "dismissed",
        "open": "open",
    }

    final_status = decision_map[payload.decision]
    finding.status = final_status

    AuditService(db).record_event(
        action=f"finding.{final_status}",
        entity_type="finding",
        entity_id=finding.id,
        user_id=user.id,
        organization_id=user.organization_id,
        details={"review_id": finding.review_id},
    )

    db.commit()

    return {
        "id": finding.id,
        "status": final_status,
        "decision": final_status,
    }


@router.patch("/{finding_id}/suggestions/{suggestion_id}/decision")
def decide_suggestion(
    finding_id: str,
    suggestion_id: str,
    payload: SuggestionDecision,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    finding = get_finding_for_user(finding_id, user, db)

    suggestion = (
        db.query(Suggestion)
        .filter(
            Suggestion.id == suggestion_id,
            Suggestion.finding_id == finding.id,
        )
        .first()
    )

    if not suggestion:
        raise HTTPException(
            status_code=404,
            detail="Suggestion not found.",
        )

    if suggestion.status != "pending":
        raise HTTPException(
            status_code=409,
            detail="This suggestion has already been reviewed.",
        )

    if payload.decision == "edited":
        edited_text = (payload.suggested_text or "").strip()

        if not edited_text:
            raise HTTPException(
                status_code=422,
                detail="Enter the edited correction before saving.",
            )

        suggestion.suggested_text = edited_text

    suggestion.status = payload.decision

    AuditService(db).record_event(
        action=f"suggestion.{payload.decision}",
        entity_type="suggestion",
        entity_id=suggestion.id,
        user_id=user.id,
        organization_id=user.organization_id,
        details={
            "finding_id": finding.id,
            "review_id": finding.review_id,
        },
    )

    db.commit()
    db.refresh(suggestion)

    return {
        "id": suggestion.id,
        "finding_id": finding.id,
        "status": suggestion.status,
        "suggested_text": suggestion.suggested_text,
    }
