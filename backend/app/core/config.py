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


# Single shared instance, imported across the app.
settings = Settings()
