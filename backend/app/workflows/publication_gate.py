
from app.workflows.approval_workflow import is_approval_complete


class PublicationGateError(Exception):
    """Raised when publication requirements are not satisfied."""


def validate_publication(
    document,
    review,
    approval,
    current_version: int,
) -> None:
    """
    Check all requirements before allowing publication.

    Publication is blocked unless the current document version
    has a completed review and explicit human approval.
    """
    if document is None:
        raise PublicationGateError("Document not found.")

    if review is None:
        raise PublicationGateError("Review not found.")

    if approval is None:
        raise PublicationGateError("Approval record not found.")

    if str(review.document_id) != str(document.id):
        raise PublicationGateError(
            "Review does not belong to this document."
        )

    if str(approval.document_id) != str(document.id):
        raise PublicationGateError(
            "Approval does not belong to this document."
        )

    if str(approval.review_id) != str(review.id):
        raise PublicationGateError(
            "Approval does not belong to this review."
        )

    if review.status != "completed":
        raise PublicationGateError(
            "The review must be completed before publication."
        )

    if not is_approval_complete(approval):
        raise PublicationGateError(
            "A valid human approval is required."
        )

    review_version = getattr(
        review,
        "document_version_number",
        None,
    )

    if review_version is None:
        raise PublicationGateError(
            "Review is missing its document version reference."
        )

    if review_version != current_version:
        raise PublicationGateError(
            "This review belongs to an older document version."
        )

    if document.current_version != current_version:
        raise PublicationGateError(
            "The supplied version is not the current document version."
        )


def can_publish(
    document,
    review,
    approval,
    current_version: int,
) -> bool:
    """Return whether a document passes the publication gate."""
    try:
        validate_publication(
            document=document,
            review=review,
            approval=approval,
            current_version=current_version,
        )
        return True
    except PublicationGateError:
        return False
