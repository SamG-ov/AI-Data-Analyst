"""Application configuration.

All settings are loaded from environment variables (or a local `.env` file)
and validated by pydantic. Import the singleton `settings` object anywhere in
the app instead of reading os.environ directly — this keeps configuration
typed, centralized, and easy to test.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # ignore unrelated env vars instead of crashing
    )

    app_name: str = "AI Data Analyst"
    environment: str = "development"

    # Secrets / external services
    anthropic_api_key: str = ""

    # CORS: which frontend origin is allowed to call this API
    frontend_origin: str = "http://localhost:3000"

    # File uploads
    upload_dir: str = "uploads"  # where uploaded datasets are stored on disk
    max_upload_bytes: int = 50 * 1024 * 1024  # 50 MB hard limit
    preview_rows: int = 10  # how many rows to return in a dataset preview


# Single shared instance, imported across the app.
settings = Settings()
