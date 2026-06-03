"""Storage service: persists uploaded files and assigns each a unique id.

This is intentionally a thin filesystem-backed layer. When we later move to
cloud storage (S3, etc.) or a database, only this module changes — callers
keep using save_upload()/path_for() unchanged.
"""

import uuid
from pathlib import Path

import pandas as pd

from app.core.config import settings

UPLOAD_DIR = Path(settings.upload_dir)


def save_upload(filename: str, content: bytes) -> tuple[str, Path]:
    """Save raw bytes to disk under a new dataset id. Returns (id, path)."""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    dataset_id = uuid.uuid4().hex
    suffix = Path(filename).suffix.lower()
    destination = UPLOAD_DIR / f"{dataset_id}{suffix}"
    destination.write_bytes(content)
    return dataset_id, destination


def save_dataframe(df: pd.DataFrame) -> tuple[str, Path]:
    """Persist a DataFrame as a new CSV-backed dataset. Returns (id, path)."""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    dataset_id = uuid.uuid4().hex
    destination = UPLOAD_DIR / f"{dataset_id}.csv"
    df.to_csv(destination, index=False)
    return dataset_id, destination


def path_for(dataset_id: str) -> Path | None:
    """Find the stored file for a dataset id, or None if it doesn't exist."""
    matches = list(UPLOAD_DIR.glob(f"{dataset_id}.*"))
    return matches[0] if matches else None
