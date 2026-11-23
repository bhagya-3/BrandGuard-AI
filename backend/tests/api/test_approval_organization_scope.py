import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_current_user, get_db
from app.core.database import Base
from app.models import (
    Approval,
    Document,
    Organization,
    Review,
    Role,
    User,
    Workspace,
)


@pytest.fixture
def approval_context():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    import app.models

    Base.metadata.create_all(bind=engine)

    TestSession = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    db = TestSession()

    def create_organization(name):
        organization = Organization(
            id=str(uuid.uuid4()),
            name=name,
            slug=f"test-{uuid.uuid4().hex[:10]}",
        )
        db.add(organization)
        db.flush()
        return organization

    def create_user(organization, name, email):
        user = User(
            id=str(uuid.uuid4()),
            organization_id=organization.id,
            email=email,
            full_name=name,
            password_hash="test-only-password-hash",
            is_active=True,
        )
        db.add(user)
        db.flush()
        return user

    org_a = create_organization("Organization A")
    org_b = create_organization("Organization B")

    global_admin = create_user(
        org_a, "Global Admin", "global-admin@example.test"
    )
    requester_a = create_user(
        org_a, "Requester A", "requester-a@example.test"
    )
    requester_b = create_user(
        org_b, "Requester B", "requester-b@example.test"
    )

    global_admin_role = Role(
        id=str(uuid.uuid4()),
        name="global_admin",
        description="Test global administrator",
    )
    db.add(global_admin_role)
    db.flush()
    global_admin.roles.append(global_admin_role)

    def create_approval(organization, requester, title):
        workspace = Workspace(
            id=str(uuid.uuid4()),
            organization_id=organization.id,
            name=f"{title} Workspace",
            created_by=requester.id,
        )
        db.add(workspace)
        db.flush()

        document = Document(
            id=str(uuid.uuid4()),
            organization_id=organization.id,
            workspace_id=workspace.id,
            uploaded_by=requester.id,
            title=title,
            original_filename="test.txt",
            mime_type="text/plain",
            file_size=10,
            storage_key=f"test/{uuid.uuid4().hex}.txt",
        )
        db.add(document)
        db.flush()

        review = Review(
            id=str(uuid.uuid4()),
            organization_id=organization.id,
            workspace_id=workspace.id,
            document_id=document.id,
            requested_by=requester.id,
            status="completed",
        )
        db.add(review)
        db.flush()

        approval = Approval(
            id=str(uuid.uuid4()),
            review_id=review.id,
            document_id=document.id,
            requested_by=requester.id,
            status="pending",
        )
        db.add(approval)
        db.flush()

        return approval

    approval_a = create_approval(
        org_a, requester_a, "Organization A document"
    )
    approval_b = create_approval(
        org_b, requester_b, "Organization B document"
    )

    db.commit()

    context = {
        "engine": engine,
        "db": db,
        "user": global_admin,
        "approval_a": approval_a,
        "approval_b": approval_b,
    }

    yield context

    db.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def approval_client(approval_context):
    from app.main import app

    db = approval_context["db"]
    user = approval_context["user"]

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


def test_global_admin_lists_only_own_organization_approvals(
    approval_client, approval_context
):
    response = approval_client.get("/api/v1/approvals/")

    assert response.status_code == 200

    approval_ids = {item["id"] for item in response.json()}

    assert approval_context["approval_a"].id in approval_ids
    assert approval_context["approval_b"].id not in approval_ids


def test_global_admin_cannot_decide_other_organization_approval(
    approval_client, approval_context
):
    approval = approval_context["approval_b"]

    response = approval_client.patch(
        f"/api/v1/approvals/{approval.id}/decision",
        json={"decision": "approved"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Approval not found."
    assert approval_context["db"].get(Approval, approval.id).status == "pending"


def test_global_admin_can_list_own_organization_approval(
    approval_client, approval_context
):
    response = approval_client.get("/api/v1/approvals/")

    assert response.status_code == 200

    approval_ids = {item["id"] for item in response.json()}

    assert approval_context["approval_a"].id in approval_ids
