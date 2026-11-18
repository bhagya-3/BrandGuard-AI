
from app.workflows.state_machine import validate_transition


class VersionInvalidationError(Exception):
    """Raised when review version invalidation fails."""


def validate_new_version(
    current_version: int,
    new_version: int,
) -> None:
    """Ensure the new document version is valid."""
    if current_version < 1 or new_version < 1:
        raise VersionInvalidationError(
            "Document versions must be positive integers."
        )

    if new_version <= current_version:
        raise VersionInvalidationError(
            "New version must be greater than the current version."
        )


def invalidate_review(review) -> bool:
    """
    Mark a completed review as superseded.

    Returns False when the review is already in a state that
    should not be invalidated.
    """
    if review is None:
        raise VersionInvalidationError("Review not found.")

    if review.status != "completed":
        return False

    validate_transition(
        "review",
        review.status,
        "superseded",
    )

    review.status = "superseded"
    return True


def invalidate_reviews_for_document(
    reviews: list,
    new_version: int,
) -> int:
    """
    Supersede completed reviews for older document versions.

    Each review must expose document_version_number.
    Add that field to your Review model and migration before
    using this function.
    """
    if new_version < 1:
        raise VersionInvalidationError(
            "Document version must be a positive integer."
        )

    invalidated_count = 0

    for review in reviews:
        review_version = getattr(
            review,
            "document_version_number",
            None,
        )

        if review_version is None:
            raise VersionInvalidationError(
                "Review model is missing document_version_number."
            )

        if review_version < new_version:
            if invalidate_review(review):
                invalidated_count += 1

    return invalidated_count


def is_review_current(
    review,
    document_version: int,
) -> bool:
    """Check whether a review belongs to the current document version."""
    review_version = getattr(
        review,
        "document_version_number",
        None,
    )

    return (
        review is not None
        and review.status == "completed"
        and review_version == document_version
    )
