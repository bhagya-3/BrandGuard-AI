
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.approval import Approval
from app.repositories.approval_repository import ApprovalRepository
from app.repositories.review_repository import ReviewRepository


class ApprovalServiceError(Exception):
    pass


class ApprovalService:

    def __init__(self, db: Session):
        self.db = db
        self.reviews = ReviewRepository(db)

    def request_approval(
        self,
        review_id: str,
        document_id: str,
        requested_by: str,
        organization_id: str,
    ) -> Approval:

        review = self.reviews.get_by_id_and_org(
            review_id,
            organization_id,
        )

        if not review:
            raise ApprovalServiceError("Review not found.")

        if review.document_id != document_id:
            raise ApprovalServiceError(
                "Review and document do not match."
            )

        if review.status != "completed":
            raise ApprovalServiceError(
                "Only completed reviews can be submitted for approval."
            )

        approval = Approval(
            review_id=review_id,
            document_id=document_id,
            requested_by=requested_by,
            status="pending",
            requested_at=datetime.now(timezone.utc),
        )

        self.db.add(approval)
        self.db.flush()

        return approval

    def decide(
        self,
        approval_id: str,
        approver_id: str,
        decision: str,
        decision_note: str | None = None,
    ) -> Approval:

        decision = decision.lower().strip()

        if decision not in {"approved", "rejected"}:
            raise ApprovalServiceError(
                "Decision must be approved or rejected."
            )

        approval = ApprovalRepository.get_by_id(
            self.db,
            approval_id,
        )

        if not approval:
            raise ApprovalServiceError(
                "Approval request not found."
            )

        if approval.status != "pending":
            raise ApprovalServiceError(
                "This approval request has already been decided."
            )

        if approval.requested_by == approver_id:
            raise ApprovalServiceError(
                "You cannot approve your own request."
            )

        ApprovalRepository.decide(
            self.db,
            approval,
            approver_id,
            decision,
            decision_note,
        )

        return approval

    def list_pending(self):
        return ApprovalRepository.list_pending(self.db)
