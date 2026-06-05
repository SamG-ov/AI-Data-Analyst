"""Dataset endpoints: upload, quality report, and auto-clean."""

from pathlib import Path

import anthropic
import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.config import settings
from app.schemas.chat import AnswerResponse, QuestionRequest
from app.schemas.cleaning import CleanResult, QualityReport
from app.schemas.dataset import DatasetSummary
from app.schemas.eda import ChartsResponse, EdaReport
from app.services import ai_service, cleaning_service, dataset_service, eda_service, storage

router = APIRouter(prefix="/datasets", tags=["datasets"])


def _load_dataset_or_404(dataset_id: str) -> pd.DataFrame:
    """Load a stored dataset by id, raising 404/400 on failure."""
    path = storage.path_for(dataset_id)
    if path is None:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    try:
        return dataset_service.load_dataframe(path)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=400, detail=f"Could not read dataset: {exc}"
        ) from exc


@router.post("", response_model=DatasetSummary, status_code=201)
async def upload_dataset(file: UploadFile = File(...)) -> DatasetSummary:
    """Upload a CSV/Excel file and get back a summary of its contents."""
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in dataset_service.SUPPORTED_SUFFIXES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix or 'unknown'}'. "
            "Allowed: CSV, XLSX, XLS.",
        )

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large (max {settings.max_upload_bytes // (1024 * 1024)} MB).",
        )

    dataset_id, path = storage.save_upload(file.filename or f"upload{suffix}", content)

    try:
        df = dataset_service.load_dataframe(path)
    except Exception as exc:  # noqa: BLE001 - surface any parse error as a 400
        path.unlink(missing_ok=True)  # don't keep an unreadable file around
        raise HTTPException(
            status_code=400, detail=f"Could not parse file: {exc}"
        ) from exc

    if df.empty:
        path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="File contains no data rows.")

    return dataset_service.summarize(df, dataset_id, file.filename or path.name)


@router.get("/{dataset_id}/quality", response_model=QualityReport)
def get_quality(dataset_id: str) -> QualityReport:
    """Return a data-quality report for a stored dataset."""
    df = _load_dataset_or_404(dataset_id)
    return cleaning_service.analyze(df)


@router.post("/{dataset_id}/clean", response_model=CleanResult)
def clean_dataset(dataset_id: str) -> CleanResult:
    """Apply conservative auto-cleaning, saving the result as a new dataset."""
    df = _load_dataset_or_404(dataset_id)
    cleaned, actions = cleaning_service.auto_clean(df)
    new_id, _ = storage.save_dataframe(cleaned)
    summary = dataset_service.summarize(cleaned, new_id, f"cleaned_{dataset_id}.csv")
    return CleanResult(dataset=summary, actions=actions)


@router.get("/{dataset_id}/eda", response_model=EdaReport)
def get_eda(dataset_id: str) -> EdaReport:
    """Return descriptive statistics for numeric and categorical columns."""
    df = _load_dataset_or_404(dataset_id)
    return eda_service.describe(df)


@router.get("/{dataset_id}/charts", response_model=ChartsResponse)
def get_charts(dataset_id: str) -> ChartsResponse:
    """Return pre-computed chart data (histograms / category bars)."""
    df = _load_dataset_or_404(dataset_id)
    return ChartsResponse(charts=eda_service.build_charts(df))


@router.post("/{dataset_id}/ask", response_model=AnswerResponse)
def ask_dataset(dataset_id: str, payload: QuestionRequest) -> AnswerResponse:
    """Answer a natural-language question about the dataset using Claude."""
    if not settings.anthropic_api_key:
        raise HTTPException(
            status_code=503,
            detail="AI features are not configured. Set ANTHROPIC_API_KEY in the backend .env.",
        )

    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question must not be empty.")

    df = _load_dataset_or_404(dataset_id)

    try:
        answer = ai_service.answer_question(df, question)
    except anthropic.APIError as exc:  # network/auth/rate-limit/etc.
        raise HTTPException(
            status_code=502, detail=f"AI service error: {exc}"
        ) from exc

    return AnswerResponse(answer=answer)
