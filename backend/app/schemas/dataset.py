"""Pydantic schemas for datasets.

These define the *contract* between backend and frontend: the exact JSON
shape the API returns. Keeping them separate from business logic means the
frontend's TypeScript types can mirror these one-to-one.
"""

from typing import Any

from pydantic import BaseModel


class ColumnInfo(BaseModel):
    """A single column's name and inferred data type."""

    name: str
    dtype: str


class DatasetSummary(BaseModel):
    """High-level summary returned right after a dataset is uploaded."""

    id: str
    filename: str
    n_rows: int
    n_columns: int
    columns: list[ColumnInfo]
    preview: list[dict[str, Any]]  # first N rows as records
