"""Tests for the /health endpoint.

Uses FastAPI's TestClient, which exercises the app in-process (no running
server needed). This is our template for testing every future endpoint.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["app"] == "AI Data Analyst"
