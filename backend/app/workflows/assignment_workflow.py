
from app.workflows.state_machine import WorkflowError


class AssignmentError(Exception):
    """Raised when review assignment is invalid."""


def validate_reviewer(
    reviewer,
    organization_id: str,
) -> None:
    """Ensure the reviewer is active and belongs to the organization."""
    if reviewer is None:
        raise AssignmentError("Reviewer not found.")

    if not getattr(reviewer, "is_active", False):
        raise AssignmentError("Reviewer account is inactive.")

    if str(getattr(reviewer, "organization_id", "")) != str(organization_id):
        raise AssignmentError(
            "Reviewer does not belong to this organization."
        )


def validate_review_assignment(
    review,
    reviewer,
) -> None:
    """Validate whether a review can be assigned."""
    if review is None:
        raise AssignmentError("Review not found.")

    if getattr(review, "status", None) not in {
        "pending",
        "in_progress",
    }:
        raise AssignmentError(
            "Only pending or in-progress reviews can be assigned."
        )

    if str(getattr(review, "organization_id", "")) != str(
        getattr(reviewer, "organization_id", "")
    ):
        raise AssignmentError(
            "Review and reviewer must belong to the same organization."
        )


def assign_review(
    review,
    reviewer,
):
    """
    Assign a review to a reviewer.

    The Review model must contain an assigned_to_id column.
    This function intentionally does not create an unpersisted
    dynamic attribute.
    """
    validate_review_assignment(review, reviewer)

    if not hasattr(type(review), "assigned_to_id"):
        raise AssignmentError(
            "Review model is missing assigned_to_id. "
            "Add this database field before enabling assignments."
        )

    review.assigned_to_id = reviewer.id
    return review


def unassign_review(review):
    """Remove the current reviewer assignment."""
    if review is None:
        raise AssignmentError("Review not found.")

    if getattr(review, "status", None) not in {
        "pending",
        "in_progress",
    }:
        raise AssignmentError(
            "This review cannot be unassigned in its current state."
        )

    if not hasattr(type(review), "assigned_to_id"):
        raise AssignmentError(
            "Review model is missing assigned_to_id."
        )

    review.assigned_to_id = None
    return review
