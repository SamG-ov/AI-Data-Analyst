"""Dataset service: parsing and summarizing tabular files with pandas.

Pure data logic with no knowledge of HTTP — easy to unit-test and reuse
from any future feature (EDA, charts, Q&A all start by loading a dataframe).
"""

import json
from pathlib import Path

import pandas as pd

from app.core.config import settings
from app.schemas.dataset import ColumnInfo, DatasetSummary

SUPPORTED_SUFFIXES = {".csv", ".xlsx", ".xls"}


def load_dataframe(path: Path) -> pd.DataFrame:
    """Read a CSV/Excel file into a DataFrame based on its extension."""
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    raise ValueError(f"Unsupported file type: {suffix}")


def summarize(df: pd.DataFrame, dataset_id: str, filename: str) -> DatasetSummary:
    """Build a JSON-safe summary (shape, column types, preview rows)."""
    columns = [
        ColumnInfo(name=str(col), dtype=str(dtype))
        for col, dtype in df.dtypes.items()
    ]

    # to_json converts NaN -> null and handles dates/numbers safely, so we
    # round-trip through it to guarantee the preview is valid JSON.
    preview_df = df.head(settings.preview_rows)
    preview = json.loads(preview_df.to_json(orient="records", date_format="iso"))

    return DatasetSummary(
        id=dataset_id,
        filename=filename,
        n_rows=int(df.shape[0]),
        n_columns=int(df.shape[1]),
        columns=columns,
        preview=preview,
    )
