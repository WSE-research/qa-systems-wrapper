"""Tests for the FastAPI application wiring in main.py."""
from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert "QA systems wrapper" in resp.json()["message"]


def test_openapi_lists_mounted_routers():
    schema = client.get("/openapi.json").json()
    assert schema["info"]["title"] == "QA Systems Wrapper"
    paths = "".join(schema["paths"].keys())
    # a sample of the included routers are mounted under their prefixes
    assert "/qanary" in paths
    assert "/platypus" in paths
