"""AI service: answer natural-language questions about a dataset with Claude.

We never send the raw file. Instead we build a compact *profile* (schema +
summary statistics + a small sample) and ask Claude to answer only from that.
The profile is marked for prompt caching, so repeated questions about the same
dataset reuse the cached prefix and only the question varies.

The API key is read from settings (loaded from .env) and passed explicitly to
the client — it stays server-side and never reaches the frontend.
"""

import anthropic
import pandas as pd

from app.core.config import settings
from app.services import eda_service

SYSTEM_PROMPT = (
    "You are a careful data analyst assistant. Answer the user's question about "
    "their dataset using ONLY the dataset profile provided. The profile contains "
    "the schema, summary statistics, and a small sample of rows — not the full "
    "data. If the answer cannot be determined from the profile alone, say so "
    "clearly and explain what additional data or computation would be needed. "
    "Be concise and concrete, and cite specific numbers from the profile when relevant."
)


class AIConfigError(RuntimeError):
    """Raised when the AI feature is used without an API key configured."""


def build_profile(df: pd.DataFrame) -> str:
    """Create a compact text profile of the dataset for the model."""
    report = eda_service.describe(df)

    lines: list[str] = [
        f"Dataset shape: {report.n_rows} rows x {report.n_columns} columns.",
        "",
        "Columns (name: dtype):",
    ]
    lines += [f"- {col}: {dtype}" for col, dtype in df.dtypes.items()]

    if report.numeric:
        lines.append("")
        lines.append("Numeric column statistics:")
        for s in report.numeric:
            lines.append(
                f"- {s.name}: count={s.count}, missing={s.missing}, mean={s.mean}, "
                f"std={s.std}, min={s.min}, q25={s.q25}, median={s.median}, "
                f"q75={s.q75}, max={s.max}"
            )

    if report.categorical:
        lines.append("")
        lines.append("Categorical column statistics:")
        for s in report.categorical:
            lines.append(
                f"- {s.name}: count={s.count}, missing={s.missing}, "
                f"unique={s.unique}, most_frequent={s.top!r} (freq={s.top_freq})"
            )

    lines.append("")
    lines.append("First rows (CSV):")
    lines.append(df.head(settings.preview_rows).to_csv(index=False).strip())

    return "\n".join(lines)


def answer_question(df: pd.DataFrame, question: str) -> str:
    """Ask Claude a question about the dataset and return the text answer."""
    if not settings.anthropic_api_key:
        raise AIConfigError("ANTHROPIC_API_KEY is not configured.")

    profile = build_profile(df)
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    message = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=settings.ai_max_tokens,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    # Stable across questions for this dataset → cache it.
                    {
                        "type": "text",
                        "text": f"Dataset profile:\n\n{profile}",
                        "cache_control": {"type": "ephemeral"},
                    },
                    # The volatile part goes last, after the cached prefix.
                    {"type": "text", "text": f"Question: {question}"},
                ],
            }
        ],
    )

    return "".join(
        block.text for block in message.content if block.type == "text"
    ).strip()
