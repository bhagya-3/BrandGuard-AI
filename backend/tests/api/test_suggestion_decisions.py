
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_current_user, get_db
from app.core.database import Base
from app.models import (
    AuditLog,
    Document,
    Finding,
    Organization,
    Review,
    Suggestion,
    User,
    Workspace,
)


@pytest.fixture
def suggestion_test_context():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Import all models before creating the test schema.
    import app.models

    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

    db = TestSession()

    organization = Organization(
        id=str(uuid.uuid4()),
        name="Test Organization",
        slug=f"test-{uuid.uuid4().hex[:10]}",
    )
    db.add(organization)
    db.flush()

    user = User(
        id=str(uuid.uuid4()),
        organization_id=organization.id,
        email=f"{uuid.uuid4().hex}@example.test",
        full_name="Test Reviewer",
        password_hash="test-only-password-hash",
        is_active=True,
    )
    db.add(user)
    db.flush()

    workspace = Workspace(
        id=str(uuid.uuid4()),
        organization_id=organization.id,
        name="Test Workspace",
        created_by=user.id,
    )
    db.add(workspace)
    db.flush()

    document = Document(
        id=str(uuid.uuid4()),
        organization_id=organization.id,
        workspace_id=workspace.id,
        uploaded_by=user.id,
        title="Test Document",
        original_filename="test.txt",
        mime_type="text/plain",
        file_size=10,
        storage_key="test/test.txt",
    )
    db.add(document)
    db.flush()

    review = Review(
        id=str(uuid.uuid4()),
        organization_id=organization.id,
        workspace_id=workspace.id,
        document_id=document.id,
        requested_by=user.id,
        status="completed",
    )
    db.add(review)
    db.flush()

    finding = Finding(
        id=str(uuid.uuid4()),
        review_id=review.id,
        document_id=document.id,
        category="readability",
        severity="medium",
        title="Long sentence",
        description="The sentence is too long.",
    )
    db.add(finding)
    db.flush()

    suggestion = Suggestion(
        id=str(uuid.uuid4()),
        finding_id=finding.id,
        created_by=user.id,
        original_text="This is the original sentence.",
        suggested_text="This is the improved sentence.",
        rationale="Improves readability.",
        status="pending",
    )
    db.add(suggestion)
    db.commit()

    yield {
        "engine": engine,
        "db": db,
        "user": user,
        "organization": organization,
        "finding": finding,
        "suggestion": suggestion,
    }

    db.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def suggestion_client(suggestion_test_context):
    from app.main import app

    db = suggestion_test_context["db"]
    user = suggestion_test_context["user"]

    def override_get_db():
        yield db

    def override_get_current_user():
        return user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_current_user, None)


def decision_url(context):
    finding = context["finding"]
    suggestion = context["suggestion"]
    return (
        f"/api/v1/findings/{finding.id}"
        f"/suggestions/{suggestion.id}/decision"
    )


def test_accept_suggestion(suggestion_client, suggestion_test_context):
    context = suggestion_test_context

    response = suggestion_client.patch(
        decision_url(context),
        json={"decision": "accepted"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "accepted"
    assert (
        response.json()["suggested_text"]
        == "This is the improved sentence."
    )

    audit = (
        context["db"].query(AuditLog)
        .filter(AuditLog.entity_id == context["suggestion"].id)
        .first()
    )
    assert audit is not None
    assert audit.action == "suggestion.accepted"


def test_edit_suggestion(suggestion_client, suggestion_test_context):
    context = suggestion_test_context
    edited_text = "This is the carefully edited sentence."

    response = suggestion_client.patch(
        decision_url(context),
        json={
            "decision": "edited",
            "suggested_text": edited_text,
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "edited"
    assert response.json()["suggested_text"] == edited_text


def test_reject_suggestion(suggestion_client, suggestion_test_context):
    context = suggestion_test_context

    response = suggestion_client.patch(
        decision_url(context),
        json={"decision": "rejected"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "rejected"


def test_edit_rejects_empty_text(suggestion_client, suggestion_test_context):
    response = suggestion_client.patch(
        decision_url(suggestion_test_context),
        json={"decision": "edited", "suggested_text": "   "},
    )

    assert response.status_code == 422


def test_already_decided_suggestion_cannot_be_changed(
    suggestion_client,
    suggestion_test_context,
):
    context = suggestion_test_context
    url = decision_url(context)

    first = suggestion_client.patch(
        url,
        json={"decision": "accepted"},
    )
    second = suggestion_client.patch(
        url,
        json={"decision": "rejected"},
    )

    assert first.status_code == 200
    assert second.status_code == 409


def test_suggestion_must_belong_to_finding(
    suggestion_client,
    suggestion_test_context,
):
    context = suggestion_test_context

    response = suggestion_client.patch(
        f"/api/v1/findings/{context['finding'].id}"
        f"/suggestions/{uuid.uuid4()}/decision",
        json={"decision": "accepted"},
    )

    assert response.status_code == 404


def test_finding_from_another_organization_is_not_accessible(
    suggestion_test_context,
):
    from app.main import app

    context = suggestion_test_context
    db = context["db"]

    other_org = Organization(
        id=str(uuid.uuid4()),
        name="Other Organization",
        slug=f"other-{uuid.uuid4().hex[:10]}",
    )
    db.add(other_org)
    db.flush()

    other_user = User(
        id=str(uuid.uuid4()),
        organization_id=other_org.id,
        email=f"{uuid.uuid4().hex}@example.test",
        full_name="Other Reviewer",
        password_hash="test-only-password-hash",
        is_active=True,
    )
    db.add(other_user)
    db.commit()

    def override_get_db():
        yield db

    def override_get_current_user():
        return other_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    try:
        with TestClient(app) as client:
            response = client.patch(
                decision_url(context),
                json={"decision": "accepted"},
            )
        assert response.status_code == 404
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(get_current_user, None)
