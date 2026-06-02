"""Tests for the /datasets upload endpoint."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_upload_csv_returns_summary():
    csv_bytes = b"name,age\nAlice,30\nBob,25\n"
    response = client.post(
        "/datasets",
        files={"file": ("people.csv", csv_bytes, "text/csv")},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["n_rows"] == 2
    assert body["n_columns"] == 2
    assert {col["name"] for col in body["columns"]} == {"name", "age"}
    assert len(body["preview"]) == 2
    assert body["preview"][0]["name"] == "Alice"
    assert body["id"]  # a non-empty id was assigned


def test_upload_rejects_unsupported_type():
    response = client.post(
        "/datasets",
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400


def test_upload_rejects_empty_file():
    response = client.post(
        "/datasets",
        files={"file": ("empty.csv", b"", "text/csv")},
    )
    assert response.status_code == 400
