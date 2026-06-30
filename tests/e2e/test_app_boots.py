"""End-to-end smoke test: the FastAPI app boots and serves health + schema."""
import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.e2e


def test_app_boots():
    import main

    with TestClient(main.app) as client:
        assert client.get("/health").status_code == 200
        schema = client.get("/openapi.json").json()
        assert schema["info"]["title"] == "QA Systems Wrapper"
