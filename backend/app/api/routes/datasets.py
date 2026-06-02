"""Dataset endpoints (upload, and later: list/get/EDA).

This layer is deliberately thin: validate the request, delegate to services,
translate failures into proper HTTP status codes.
"""

from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.config import settings
from app.schemas.dataset import DatasetSummary
from app.services import dataset_service, storage

router = APIRouter(prefix="/datasets", tags=["datasets"])


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
