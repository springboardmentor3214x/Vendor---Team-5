class Settings:
    PROJECT_NAME = "Vendor Reliability Intelligence Platform"
    API_VERSION = "0.1.0"
    ALLOWED_ORIGINS = [
        "http://localhost:4200",
        "http://127.0.0.1:4200",
    ]
    DATABASE_URL = "postgresql://postgres:password@localhost:5432/vendoriq"


settings = Settings()