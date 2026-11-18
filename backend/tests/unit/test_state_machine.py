import pytest

from app.workflows.state_machine import (
    can_transition,
    validate_transition,
    transition_status,
)


def test_valid_document_transition():
    assert can_transition("document", "uploaded", "processing")


def test_invalid_document_transition():
    assert not can_transition("document", "uploaded", "published")


def test_valid_review_transition():
    assert can_transition("review", "pending", "in_progress")


def test_completed_review_transition():
    assert can_transition("review", "in_progress", "completed")


def test_invalid_transition_raises_error():
    with pytest.raises((ValueError, Exception)):
        validate_transition("review", "pending", "published")


def test_transition_status():
    result = transition_status("review", "pending", "in_progress")

    assert result == "in_progress"