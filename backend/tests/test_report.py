"""Tests for the /report download endpoint."""

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


def test_report_downloads_html():
    dataset = _upload()

    response = client.get(f"/datasets/{dataset['id']}/report")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "attachment" in response.headers.get("content-disposition", "")
    assert "Data Analysis Report" in response.text
    assert "revenue" in response.text


def test_report_includes_insights_when_requested(monkeypatch):
    monkeypatch.setattr(settings, "anthropic_api_key", "test-key")
    monkeypatch.setattr(ai_service, "generate_insights", lambda df: "INSIGHT-XYZ")
    dataset = _upload()

    response = client.get(f"/datasets/{dataset['id']}/report?include_insights=true")
    assert response.status_code == 200
    assert "INSIGHT-XYZ" in response.text


def test_report_insights_requires_api_key(monkeypatch):
    monkeypatch.setattr(settings, "anthropic_api_key", "")
    dataset = _upload()

    response = client.get(f"/datasets/{dataset['id']}/report?include_insights=true")
    assert response.status_code == 503


def test_report_unknown_dataset_returns_404():
    response = client.get("/datasets/nope/report")
    assert response.status_code == 404
