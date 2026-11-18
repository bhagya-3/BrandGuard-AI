# backend/tests/conftest.py

import os

import pytest
from fastapi.testclient import TestClient

# Provide test-only secrets before importing application modules.
os.environ.setdefault(
    "JWT_SECRET_KEY",
    "test-only-jwt-secret-key-with-at-least-32-characters",
)
os.environ.setdefault("DATA_ENCRYPTION_KEY", "")
os.environ.setdefault("DEBUG", "True")


@pytest.fixture
def client():
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_text():
    return (
        "Welcome to our company. "
        "We provide reliable customer support. "
        "Please contact our team for more information."
    )


@pytest.fixture
def sample_file_content():
    return b"BrandGuard AI test document."