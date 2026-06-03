"""Exploratory data analysis: descriptive statistics and chart data.

Pure pandas/numpy logic, no HTTP. The "charts" here are just computed
data (labels + counts) — rendering is the frontend's job.
"""

from typing import Any

import numpy as np
import pandas as pd

from app.schemas.eda import (
    CategoricalStats,
    Chart,
    EdaReport,
    NumericStats,
)

# Cap categories/bins so payloads stay small and charts stay readable.
MAX_BINS = 10
MAX_CATEGORIES = 10


def _f(value: Any) -> float | None:
    """Round to a float, or None for NaN/None (so it's valid JSON)."""
    if value is None or pd.isna(value):
        return None
    return round(float(value), 3)


def describe(df: pd.DataFrame) -> EdaReport:
    """Compute per-column descriptive statistics."""
    numeric: list[NumericStats] = []
    for col in df.select_dtypes(include="number").columns:
        series = df[col]
        non_null = series.dropna()
        numeric.append(
            NumericStats(
                name=str(col),
                count=int(non_null.count()),
                missing=int(series.isna().sum()),
                mean=_f(non_null.mean()),
                std=_f(non_null.std()),
                min=_f(non_null.min()),
                q25=_f(non_null.quantile(0.25)),
                median=_f(non_null.median()),
                q75=_f(non_null.quantile(0.75)),
                max=_f(non_null.max()),
            )
        )

    categorical: list[CategoricalStats] = []
    for col in df.select_dtypes(exclude="number").columns:
        series = df[col]
        non_null = series.dropna()
        counts = non_null.value_counts()
        categorical.append(
            CategoricalStats(
                name=str(col),
                count=int(non_null.count()),
                missing=int(series.isna().sum()),
                unique=int(non_null.nunique()),
                top=str(counts.index[0]) if not counts.empty else None,
                top_freq=int(counts.iloc[0]) if not counts.empty else 0,
            )
        )

    return EdaReport(
        n_rows=int(df.shape[0]),
        n_columns=int(df.shape[1]),
        numeric=numeric,
        categorical=categorical,
    )


def build_charts(df: pd.DataFrame) -> list[Chart]:
    """Build one chart per column: histogram (numeric) or bar (categorical)."""
    charts: list[Chart] = []
    for col in df.columns:
        series = df[col]
        if pd.api.types.is_numeric_dtype(series):
            chart = _histogram(col, series)
        else:
            chart = _bar(col, series)
        if chart is not None:
            charts.append(chart)
    return charts


def _histogram(col: Any, series: pd.Series) -> Chart | None:
    values = series.dropna()
    if values.empty:
        return None
    bins = min(MAX_BINS, max(1, int(values.nunique())))
    counts, edges = np.histogram(values, bins=bins)
    labels = [f"{edges[i]:.3g}–{edges[i + 1]:.3g}" for i in range(len(counts))]
    return Chart(
        column=str(col),
        type="histogram",
        title=f"Distribution of {col}",
        labels=labels,
        values=[int(c) for c in counts],
    )


def _bar(col: Any, series: pd.Series) -> Chart | None:
    counts = series.dropna().value_counts().head(MAX_CATEGORIES)
    if counts.empty:
        return None
    return Chart(
        column=str(col),
        type="bar",
        title=f"Top values: {col}",
        labels=[str(i) for i in counts.index],
        values=[int(v) for v in counts.values],
    )
