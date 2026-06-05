"""Report service: render a self-contained HTML report for a dataset.

Reuses the existing analysis services (dataset/cleaning/eda) and optionally
the AI insights. All CSS is inlined so the downloaded file stands alone and
can be opened in any browser or printed to PDF.
"""

import html
from datetime import datetime, timezone

import pandas as pd

from app.core.config import settings
from app.schemas.eda import Chart
from app.services import cleaning_service, dataset_service, eda_service

_CSS = """
* { box-sizing: border-box; }
body { font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
       color: #1f2937; margin: 0; padding: 2.5rem; max-width: 960px;
       margin-inline: auto; line-height: 1.5; }
h1 { font-size: 1.8rem; margin-bottom: 0.25rem; }
h2 { font-size: 1.15rem; margin-top: 2rem; border-bottom: 1px solid #e5e7eb;
     padding-bottom: 0.3rem; }
h3 { font-size: 1rem; margin: 1.2rem 0 0.5rem; }
.muted { color: #6b7280; font-size: 0.85rem; }
table { border-collapse: collapse; width: 100%; font-size: 0.85rem; margin-top: 0.5rem; }
th, td { text-align: left; padding: 0.4rem 0.6rem; border-bottom: 1px solid #f0f0f0; }
th { background: #f9fafb; }
.stats { display: flex; gap: 2rem; margin-top: 0.5rem; }
.stat .n { font-size: 1.5rem; font-weight: 600; }
.stat .l { font-size: 0.75rem; color: #6b7280; }
.chart { margin: 1rem 0; }
.bar-row { display: flex; align-items: center; gap: 0.5rem; font-size: 0.75rem; margin: 0.2rem 0; }
.bar-label { width: 11rem; text-align: right; color: #6b7280; overflow: hidden;
             white-space: nowrap; text-overflow: ellipsis; }
.bar-track { flex: 1; background: #f0f0f0; border-radius: 3px; height: 0.9rem; }
.bar-fill { display: block; height: 0.9rem; background: #3b82f6; border-radius: 3px; }
.bar-value { width: 3rem; color: #6b7280; }
.insights { white-space: pre-wrap; background: #f9fafb; padding: 1rem;
            border-radius: 6px; font-size: 0.9rem; }
"""


def _esc(value: object) -> str:
    return html.escape(str(value))


def _fmt(value: float | None) -> str:
    return "—" if value is None else _esc(value)


def _quality_section(df: pd.DataFrame) -> str:
    report = cleaning_service.analyze(df)
    return (
        "<h2>Data quality</h2>"
        '<div class="stats">'
        f'<div class="stat"><div class="n">{report.duplicate_rows}</div>'
        '<div class="l">Duplicate rows</div></div>'
        f'<div class="stat"><div class="n">{report.total_missing}</div>'
        '<div class="l">Missing values</div></div>'
        "</div>"
    )


def _numeric_section(df: pd.DataFrame) -> str:
    stats = eda_service.describe(df).numeric
    if not stats:
        return ""
    head = (
        "<tr><th>Column</th><th>Count</th><th>Missing</th><th>Mean</th>"
        "<th>Std</th><th>Min</th><th>25%</th><th>Median</th><th>75%</th><th>Max</th></tr>"
    )
    rows = "".join(
        f"<tr><td>{_esc(s.name)}</td><td>{s.count}</td><td>{s.missing}</td>"
        f"<td>{_fmt(s.mean)}</td><td>{_fmt(s.std)}</td><td>{_fmt(s.min)}</td>"
        f"<td>{_fmt(s.q25)}</td><td>{_fmt(s.median)}</td><td>{_fmt(s.q75)}</td>"
        f"<td>{_fmt(s.max)}</td></tr>"
        for s in stats
    )
    return f"<h3>Numeric columns</h3><table>{head}{rows}</table>"


def _categorical_section(df: pd.DataFrame) -> str:
    stats = eda_service.describe(df).categorical
    if not stats:
        return ""
    head = (
        "<tr><th>Column</th><th>Count</th><th>Missing</th>"
        "<th>Unique</th><th>Top</th><th>Top freq</th></tr>"
    )
    rows = "".join(
        f"<tr><td>{_esc(s.name)}</td><td>{s.count}</td><td>{s.missing}</td>"
        f"<td>{s.unique}</td><td>{_esc(s.top) if s.top is not None else '—'}</td>"
        f"<td>{s.top_freq}</td></tr>"
        for s in stats
    )
    return f"<h3>Categorical columns</h3><table>{head}{rows}</table>"


def _chart_html(chart: Chart) -> str:
    max_v = max(chart.values) if chart.values else 1
    rows = ""
    for label, value in zip(chart.labels, chart.values):
        pct = (value / max_v * 100) if max_v else 0
        rows += (
            '<div class="bar-row">'
            f'<span class="bar-label">{_esc(label)}</span>'
            f'<span class="bar-track"><span class="bar-fill" style="width:{pct:.1f}%"></span></span>'
            f'<span class="bar-value">{value}</span>'
            "</div>"
        )
    return f'<div class="chart"><h3>{_esc(chart.title)}</h3>{rows}</div>'


def _charts_section(df: pd.DataFrame) -> str:
    charts = eda_service.build_charts(df)
    if not charts:
        return ""
    return "<h2>Charts</h2>" + "".join(_chart_html(c) for c in charts)


def _preview_section(df: pd.DataFrame, dataset_id: str) -> str:
    summary = dataset_service.summarize(df, dataset_id, "dataset")
    head = "<tr>" + "".join(f"<th>{_esc(c.name)}</th>" for c in summary.columns) + "</tr>"
    rows = ""
    for record in summary.preview:
        cells = "".join(
            f"<td>{_esc(record.get(c.name)) if record.get(c.name) not in (None, '') else '—'}</td>"
            for c in summary.columns
        )
        rows += f"<tr>{cells}</tr>"
    return f"<h2>Data preview</h2><table>{head}{rows}</table>"


def build_html_report(
    df: pd.DataFrame, dataset_id: str, *, insights: str | None = None
) -> str:
    """Assemble the full self-contained HTML report document."""
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    insights_section = ""
    if insights:
        insights_section = f'<h2>AI insights</h2><div class="insights">{_esc(insights)}</div>'

    body = (
        f"<h1>Data Analysis Report</h1>"
        f'<p class="muted">{df.shape[0]} rows &times; {df.shape[1]} columns '
        f"&middot; generated {generated} by {_esc(settings.app_name)}</p>"
        f"{_quality_section(df)}"
        "<h2>Statistics</h2>"
        f"{_numeric_section(df)}"
        f"{_categorical_section(df)}"
        f"{_charts_section(df)}"
        f"{_preview_section(df, dataset_id)}"
        f"{insights_section}"
    )

    return (
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        "<title>Data Analysis Report</title>"
        f"<style>{_CSS}</style></head><body>{body}</body></html>"
    )
