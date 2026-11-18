import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.models
from app.core.database import Base
from app.services.auth_service import AuthService, AuthServiceError


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    with Session(engine) as session:
        yield session
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def test_registration_and_login_with_normalized_email(db_session):
    service = AuthService(db_session)
    password = "BrandGuard-Test-Password-2026!"

    user = service.register(
        "Auth Test Organization",
        "Test User",
        "  TEST-USER@EXAMPLE.COM ",
        password,
    )
    db_session.commit()

    result = service.login("test-user@example.com", password)

    assert user.email == "test-user@example.com"
    assert result["user"].id == user.id
    assert result["access_token"]

    with pytest.raises(AuthServiceError, match="Invalid email or password"):
        service.login("test-user@example.com", "incorrect-password")
