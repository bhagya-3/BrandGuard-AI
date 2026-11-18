
from typing import Dict, Set


class WorkflowError(Exception):
    """Raised when a workflow operation is invalid."""


WORKFLOW_TRANSITIONS: Dict[str, Dict[str, Set[str]]] = {
    "document": {
        "uploaded": {"processing", "deleted"},
        "processing": {"processed", "processing_failed"},
        "processed": {"processing", "review_pending", "deleted"},
        "processing_failed": {"processing", "deleted"},
        "review_pending": {"processed", "deleted"},
    },
    "review": {
        "pending": {"in_progress", "cancelled"},
        "in_progress": {"completed", "failed", "cancelled"},
        "completed": {"in_progress", "superseded"},
        "failed": {"in_progress", "cancelled"},
        "cancelled": set(),
        "superseded": set(),
    },
    "approval": {
        "pending": {"approved", "rejected", "cancelled"},
        "approved": set(),
        "rejected": {"pending"},
        "cancelled": set(),
    },
    "publication": {
        "draft": {"published", "cancelled"},
        "published": {"revoked"},
        "revoked": set(),
        "cancelled": set(),
    },
}


def can_transition(
    workflow_type: str,
    current_status: str,
    new_status: str,
) -> bool:
    """Check whether a status transition is allowed."""
    transitions = WORKFLOW_TRANSITIONS.get(workflow_type)

    if transitions is None:
        raise WorkflowError(f"Unknown workflow type: {workflow_type}")

    allowed = transitions.get(current_status)

    if allowed is None:
        raise WorkflowError(
            f"Unknown {workflow_type} status: {current_status}"
        )

    return new_status in allowed


def validate_transition(
    workflow_type: str,
    current_status: str,
    new_status: str,
) -> None:
    """Raise an error if a transition is not permitted."""
    if not can_transition(workflow_type, current_status, new_status):
        raise WorkflowError(
            f"Cannot change {workflow_type} status "
            f"from '{current_status}' to '{new_status}'."
        )


def transition_status(
    workflow_type_or_entity,
    current_status_or_workflow_type,
    new_status_or_none=None,
):
    """Validate a workflow transition and return the next status.

    Supports both the callable-style ``transition_status(entity, workflow_type, new_status)``
    and the simpler ``transition_status(workflow_type, current_status, new_status)`` API.
    """
    if new_status_or_none is None:
        raise TypeError("transition_status requires workflow_type, current_status, and new_status.")

    if isinstance(workflow_type_or_entity, str):
        workflow_type = workflow_type_or_entity
        current_status = current_status_or_workflow_type
        new_status = new_status_or_none

        validate_transition(
            workflow_type,
            current_status,
            new_status,
        )
        return new_status

    entity = workflow_type_or_entity
    workflow_type = current_status_or_workflow_type
    new_status = new_status_or_none
    current_status = getattr(entity, "status", None)

    if not current_status:
        raise WorkflowError("Entity does not have a valid status.")

    validate_transition(
        workflow_type,
        current_status,
        new_status,
    )

    entity.status = new_status
    return entity


def get_allowed_transitions(
    workflow_type: str,
    current_status: str,
) -> list:
    """Return all valid next statuses."""
    transitions = WORKFLOW_TRANSITIONS.get(workflow_type)

    if transitions is None:
        raise WorkflowError(f"Unknown workflow type: {workflow_type}")

    if current_status not in transitions:
        raise WorkflowError(f"Unknown status: {current_status}")

    return sorted(transitions[current_status])
