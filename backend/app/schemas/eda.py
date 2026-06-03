"""Schemas for exploratory data analysis (statistics + chart data)."""

from pydantic import BaseModel


class NumericStats(BaseModel):
    """Descriptive statistics for a numeric column."""

    name: str
    count: int
    missing: int
    mean: float | None
    std: float | None
    min: float | None
    q25: float | None
    median: float | None
    q75: float | None
    max: float | None


class CategoricalStats(BaseModel):
    """Descriptive statistics for a non-numeric column."""

    name: str
    count: int
    missing: int
    unique: int
    top: str | None
    top_freq: int


class EdaReport(BaseModel):
    """Full EDA: numeric and categorical column statistics."""

    n_rows: int
    n_columns: int
    numeric: list[NumericStats]
    categorical: list[CategoricalStats]


class Chart(BaseModel):
    """Pre-computed chart data, ready for any renderer to draw.

    `type` is "histogram" (numeric distribution) or "bar" (category counts).
    `labels`/`values` are parallel arrays.
    """

    column: str
    type: str
    title: str
    labels: list[str]
    values: list[int]


class ChartsResponse(BaseModel):
    charts: list[Chart]
