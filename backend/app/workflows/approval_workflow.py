
from datetime import datetime, timezone

from app.workflows.state_machine import validate_transition


class ApprovalWorkflowError(Exception):
    """Raised when an approval workflow operation is invalid."""


def validate_approval_request(review) -> None:
    """Only completed reviews can enter the approval process."""
    if review is None:
        raise ApprovalWorkflowError("Review not found.")

    if review.status != "completed":
        raise ApprovalWorkflowError(
            "Only completed reviews can be submitted for approval."
        )


def validate_approver(
    approval,
    approver,
) -> None:
    """Validate the human approver."""
    if approval is None:
        raise ApprovalWorkflowError("Approval record not found.")

    if approver is None:
        raise ApprovalWorkflowError("Approver not found.")

    if not getattr(approver, "is_active", False):
        raise ApprovalWorkflowError("Approver account is inactive.")

    if str(approval.requested_by) == str(approver.id):
        raise ApprovalWorkflowError(
            "The requester cannot approve their own request."
        )


def decide_approval(
    approval,
    approver,
    decision: str,
    decision_note: str = None,
):
    """
    Approve or reject an approval request.

    This function does not commit the database transaction.
    The service layer owns commits and rollbacks.
    """
    decision = decision.lower().strip()

    if decision not in {"approved", "rejected"}:
        raise ApprovalWorkflowError(
            "Decision must be 'approved' or 'rejected'."
        )

    validate_approver(approval, approver)

    validate_transition(
        "approval",
        approval.status,
        decision,
    )

    approval.status = decision
    approval.approver_id = approver.id
    approval.decision_note = decision_note
    approval.decided_at = datetime.now(timezone.utc)

    return approval


def cancel_approval(approval):
    """Cancel an approval request that is still pending."""
    if approval is None:
        raise ApprovalWorkflowError("Approval record not found.")

    validate_transition(
        "approval",
        approval.status,
        "cancelled",
    )

    approval.status = "cancelled"
    approval.decided_at = datetime.now(timezone.utc)

    return approval


def is_approval_complete(approval) -> bool:
    """Return True when the approval has been granted."""
    return (
        approval is not None
        and approval.status == "approved"
        and approval.approver_id is not None
        and approval.decided_at is not None
    )
