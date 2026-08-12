from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Vendor Reliability Intelligence Platform"
    API_VERSION: str = "0.1.0"
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:4200",
        "http://127.0.0.1:4200",
    ]
    # A local-only default keeps first-time setup clear; .env/environment wins.
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/vendor_db"
    SECRET_KEY: str = "change_this_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Module 9: background scans create in-app reminders for expiring
    # contracts/certifications and delayed deliveries.  The interval is kept
    # configurable so local development and deployment can choose a cadence
    # without changing application code.
    NOTIFICATION_SCHEDULER_ENABLED: bool = True
    NOTIFICATION_SCHEDULER_INTERVAL_MINUTES: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
