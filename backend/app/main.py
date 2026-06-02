"""FastAPI application entry point.

Creates the app, wires up CORS so the Next.js frontend can call it, and
exposes a /health endpoint used for liveness checks (locally and in
deployment). Feature routers (upload, EDA, chat, etc.) will be added in
later steps.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import datasets
from app.core.config import settings

app = FastAPI(title=settings.app_name, version="0.1.0")

# Allow the frontend (different origin/port) to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Liveness check. Returns 200 with basic service info when the app is up."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment,
    }


# Feature routers
app.include_router(datasets.router)
