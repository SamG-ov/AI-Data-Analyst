"""Tests for the EDA statistics and chart-data endpoints."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _upload(csv_bytes: bytes, name: str = "data.csv") -> dict:
    response = client.post(
        "/datasets",
        files={"file": (name, csv_bytes, "text/csv")},
    )
    assert response.status_code == 201
    return response.json()


def test_eda_reports_numeric_and_categorical_stats():
    dataset = _upload(b"city,score\nNYC,10\nLA,20\nNYC,30\n")

    response = client.get(f"/datasets/{dataset['id']}/eda")
    assert response.status_code == 200
    body = response.json()

    score = next(c for c in body["numeric"] if c["name"] == "score")
    assert score["mean"] == 20.0
    assert score["min"] == 10.0
    assert score["max"] == 30.0

    city = next(c for c in body["categorical"] if c["name"] == "city")
    assert city["top"] == "NYC"
    assert city["top_freq"] == 2
    assert city["unique"] == 2


def test_charts_include_histogram_and_bar():
    dataset = _upload(b"city,score\nNYC,10\nLA,20\nNYC,30\n")

    response = client.get(f"/datasets/{dataset['id']}/charts")
    assert response.status_code == 200
    charts = response.json()["charts"]

    types = {c["type"] for c in charts}
    assert "histogram" in types  # score
    assert "bar" in types  # city
    for chart in charts:
        assert len(chart["labels"]) == len(chart["values"])


def test_eda_unknown_dataset_returns_404():
    assert client.get("/datasets/nope/eda").status_code == 404
