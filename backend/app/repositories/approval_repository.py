
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.approval import Approval


class ApprovalRepository:

    @staticmethod
    def get_by_id(db: Session, approval_id: str):
        return (
            db.query(Approval)
            .filter(Approval.id == approval_id)
            .first()
        )

    @staticmethod
    def list_by_review(
        db: Session,
        review_id: str,
        skip: int = 0,
        limit: int = 50,
    ):
        return (
            db.query(Approval)
            .filter(Approval.review_id == review_id)
            .order_by(Approval.requested_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def list_pending(
        db: Session,
        approver_id: str = None,
        skip: int = 0,
        limit: int = 50,
    ):
        query = db.query(Approval).filter(
            Approval.status == "pending"
        )

        if approver_id:
            query = query.filter(
                Approval.approver_id == approver_id
            )

        return (
            query.order_by(Approval.requested_at.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def create(db: Session, approval_data: dict):
        approval = Approval(**approval_data)
        db.add(approval)
        db.flush()
        return approval

    @staticmethod
    def decide(
        db: Session,
        approval: Approval,
        approver_id: str,
        decision: str,
        decision_note: str = None,
    ):
        if approval.status != "pending":
            raise ValueError(
                "Only pending approval requests can be decided."
            )

        allowed_decisions = {"approved", "rejected"}

        if decision not in allowed_decisions:
            raise ValueError("Invalid approval decision.")

        approval.approver_id = approver_id
        approval.status = decision
        approval.decision_note = decision_note
        approval.decided_at = datetime.now(timezone.utc)

        db.flush()
        return approval

    @staticmethod
    def delete(db: Session, approval: Approval):
        db.delete(approval)
        db.flush()
