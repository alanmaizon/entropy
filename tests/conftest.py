"""
Shared pytest fixtures for the Enthropy test suite.
"""

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client() -> TestClient:
    """Return a synchronous test client for the FastAPI app."""
    return TestClient(app)
