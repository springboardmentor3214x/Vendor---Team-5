from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    auth,
    communications,
    contracts,
    dashboard,
    notifications,
    performance,
    procurement,
    reliability,
    reports,
    vendors,
    certifications,
    compliance,
    documents,
)
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
    description="Vendor Reliability Intelligence Platform API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = getattr(settings, "API_PREFIX", "")

app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(vendors.router, prefix=API_PREFIX)
app.include_router(procurement.router, prefix=API_PREFIX)
app.include_router(performance.router, prefix=API_PREFIX)
app.include_router(reliability.router, prefix=API_PREFIX)
app.include_router(contracts.router, prefix=API_PREFIX)
app.include_router(dashboard.router, prefix=API_PREFIX)
app.include_router(communications.router, prefix=API_PREFIX)
app.include_router(notifications.router, prefix=API_PREFIX)
app.include_router(reports.router, prefix=API_PREFIX)
app.include_router(certifications.router, prefix=API_PREFIX)
app.include_router(compliance.router, prefix=API_PREFIX)
app.include_router(documents.router, prefix=API_PREFIX)


@app.get("/", tags=["System"])
def read_root():
    return {
        "message": "Vendor Reliability Intelligence Platform API",
        "status": "running",
        "version": settings.API_VERSION,
        "modules": [
            "authentication",
            "vendors",
            "procurement",
            "performance",
            "reliability",
            "contracts",
            "communications",
            "notifications",
            "reports",
            "certifications",
            "compliance",
            "documents"
        ],
    }

@app.get("/health")
def health_check():
    return {
        "status": "success",
        "message": "Backend is healthy",
    }
