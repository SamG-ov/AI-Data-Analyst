"""Tests for the /insights endpoint (AI call is mocked)."""

from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.services import ai_service

client = TestClient(app)


def _upload(csv_bytes: bytes = b"region,revenue\nNorth,100\nSouth,50\n") -> dict:
    response = client.post(
        "/datasets",
        files={"file": ("data.csv", csv_bytes, "text/csv")},
    )
    assert response.status_code == 201
    return response.json()


def test_insights_returns_report(monkeypatch):
    monkeypatch.setattr(settings, "anthropic_api_key", "test-key")
    monkeypatch.setattr(
        ai_service,
        "generate_insights",
        lambda df: "Summary\n- North leads revenue.",
    )
    dataset = _upload()

    response = client.post(f"/datasets/{dataset['id']}/insights")
    assert response.status_code == 200
    assert "North" in response.json()["report"]


def test_insights_requires_api_key(monkeypatch):
    monkeypatch.setattr(settings, "anthropic_api_key", "")
    dataset = _upload()

    response = client.post(f"/datasets/{dataset['id']}/insights")
    assert response.status_code == 503


def test_insights_unknown_dataset_returns_404(monkeypatch):
    monkeypatch.setattr(settings, "anthropic_api_key", "test-key")
    monkeypatch.setattr(ai_service, "generate_insights", lambda df: "x")

    response = client.post("/datasets/nope/insights")
    assert response.status_code == 404
