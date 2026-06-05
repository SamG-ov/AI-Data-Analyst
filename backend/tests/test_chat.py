"""Tests for the /ask Q&A endpoint.

These tests mock the AI call — they never contact the real Anthropic API
(which would be slow, flaky, and cost money). We test the endpoint wiring,
validation, and configuration handling instead.
"""

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


def test_ask_returns_answer(monkeypatch):
    monkeypatch.setattr(settings, "anthropic_api_key", "test-key")
    monkeypatch.setattr(
        ai_service,
        "answer_question",
        lambda df, question: "The North region has the highest revenue.",
    )
    dataset = _upload()

    response = client.post(
        f"/datasets/{dataset['id']}/ask",
        json={"question": "Which region has the highest revenue?"},
    )
    assert response.status_code == 200
    assert "North" in response.json()["answer"]


def test_ask_requires_api_key(monkeypatch):
    monkeypatch.setattr(settings, "anthropic_api_key", "")
    dataset = _upload()

    response = client.post(
        f"/datasets/{dataset['id']}/ask",
        json={"question": "Anything?"},
    )
    assert response.status_code == 503


def test_ask_rejects_blank_question(monkeypatch):
    monkeypatch.setattr(settings, "anthropic_api_key", "test-key")
    dataset = _upload()

    response = client.post(
        f"/datasets/{dataset['id']}/ask",
        json={"question": "   "},
    )
    assert response.status_code == 400


def test_ask_unknown_dataset_returns_404(monkeypatch):
    monkeypatch.setattr(settings, "anthropic_api_key", "test-key")
    monkeypatch.setattr(ai_service, "answer_question", lambda df, question: "x")

    response = client.post(
        "/datasets/nope/ask",
        json={"question": "Which region wins?"},
    )
    assert response.status_code == 404
