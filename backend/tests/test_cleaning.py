"""Tests for the quality-report and auto-clean endpoints."""

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


def test_quality_report_counts_duplicates_and_missing():
    csv = b"name,age\nAlice,30\nAlice,30\nBob,\n"
    dataset = _upload(csv)

    response = client.get(f"/datasets/{dataset['id']}/quality")
    assert response.status_code == 200
    body = response.json()

    assert body["duplicate_rows"] == 1
    age = next(c for c in body["columns"] if c["name"] == "age")
    assert age["missing"] == 1


def test_clean_drops_duplicates_into_new_dataset():
    csv = b"name,age\nAlice,30\nAlice,30\nBob,25\n"
    dataset = _upload(csv)

    response = client.post(f"/datasets/{dataset['id']}/clean")
    assert response.status_code == 200
    body = response.json()

    # Cleaned dataset has duplicates removed and a brand-new id.
    assert body["dataset"]["n_rows"] == 2
    assert body["dataset"]["id"] != dataset["id"]
    assert any(a["action"] == "drop_duplicates" for a in body["actions"])


def test_quality_unknown_dataset_returns_404():
    response = client.get("/datasets/doesnotexist/quality")
    assert response.status_code == 404
