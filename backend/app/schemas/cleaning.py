"""Schemas for data-quality reporting and cleaning."""

from pydantic import BaseModel

from app.schemas.dataset import DatasetSummary


class ColumnQuality(BaseModel):
    """Per-column data-quality metrics."""

    name: str
    dtype: str
    missing: int
    missing_pct: float
    n_unique: int
    is_constant: bool  # only one distinct value (often uninformative)


class QualityReport(BaseModel):
    """Dataset-wide quality assessment."""

    n_rows: int
    n_columns: int
    duplicate_rows: int
    total_missing: int
    columns: list[ColumnQuality]


class CleanAction(BaseModel):
    """A single transformation applied during cleaning."""

    action: str
    detail: str


class CleanResult(BaseModel):
    """The cleaned dataset's summary plus the list of actions performed."""

    dataset: DatasetSummary
    actions: list[CleanAction]
