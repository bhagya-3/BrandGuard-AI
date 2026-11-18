
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.finding import Finding
from app.models.review import Review
from app.models.user import User
from app.services.audit_service import AuditService


router = APIRouter()


class FindingDecision(BaseModel):
    decision: str = Field(
        pattern="^(resolved|dismissed|open|accepted|rejected|edited)$"
    )


@router.patch("/{finding_id}/decision")
def decide_finding(
    finding_id: str,
    payload: FindingDecision,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
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

    # Keep compatibility with older frontend requests.
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
