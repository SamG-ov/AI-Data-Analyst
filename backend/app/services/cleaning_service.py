"""Data-quality analysis and conservative auto-cleaning.

Design choice: auto_clean only performs *safe* operations (whitespace,
all-empty rows/columns, exact duplicate rows). It deliberately does NOT
impute missing values or coerce types, because those change the meaning of
the data and should be explicit, user-driven decisions. Missing values are
reported by analyze() so the user can see them.
"""

import pandas as pd

from app.schemas.cleaning import CleanAction, ColumnQuality, QualityReport


def analyze(df: pd.DataFrame) -> QualityReport:
    """Compute dataset-wide and per-column quality metrics."""
    n_rows = int(df.shape[0])

    columns: list[ColumnQuality] = []
    for col in df.columns:
        series = df[col]
        missing = int(series.isna().sum())
        n_unique = int(series.nunique(dropna=True))
        columns.append(
            ColumnQuality(
                name=str(col),
                dtype=str(series.dtype),
                missing=missing,
                missing_pct=round(missing / n_rows * 100, 2) if n_rows else 0.0,
                n_unique=n_unique,
                is_constant=n_unique <= 1,
            )
        )

    return QualityReport(
        n_rows=n_rows,
        n_columns=int(df.shape[1]),
        duplicate_rows=int(df.duplicated().sum()),
        total_missing=int(df.isna().sum().sum()),
        columns=columns,
    )


def auto_clean(df: pd.DataFrame) -> tuple[pd.DataFrame, list[CleanAction]]:
    """Apply conservative cleaning. Returns (cleaned_df, actions_taken)."""
    df = df.copy()
    actions: list[CleanAction] = []

    # 1. Trim whitespace on text columns.
    text_cols = df.select_dtypes(include="object").columns
    if len(text_cols) > 0:
        for col in text_cols:
            df[col] = df[col].map(lambda v: v.strip() if isinstance(v, str) else v)
        actions.append(
            CleanAction(
                action="trim_whitespace",
                detail=f"Trimmed leading/trailing whitespace in {len(text_cols)} text column(s).",
            )
        )

    # 2. Drop all-empty columns.
    empty_cols = [c for c in df.columns if df[c].isna().all()]
    if empty_cols:
        df = df.drop(columns=empty_cols)
        actions.append(
            CleanAction(
                action="drop_empty_columns",
                detail=f"Dropped {len(empty_cols)} all-empty column(s): {', '.join(map(str, empty_cols))}.",
            )
        )

    # 3. Drop all-empty rows.
    before = len(df)
    df = df.dropna(how="all")
    if len(df) < before:
        actions.append(
            CleanAction(
                action="drop_empty_rows",
                detail=f"Dropped {before - len(df)} all-empty row(s).",
            )
        )

    # 4. Drop exact duplicate rows.
    before = len(df)
    df = df.drop_duplicates()
    if len(df) < before:
        actions.append(
            CleanAction(
                action="drop_duplicates",
                detail=f"Dropped {before - len(df)} duplicate row(s).",
            )
        )

    if not actions:
        actions.append(
            CleanAction(action="none", detail="No cleanable issues found.")
        )

    return df.reset_index(drop=True), actions
