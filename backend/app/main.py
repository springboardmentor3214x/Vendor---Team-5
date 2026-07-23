from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    auth,
    communications,
    contracts,
    notifications,
    performance,
    procurement,
    reports,
    vendors,
)
from app.core.config import settings

try:
    from app.api import reliability
    HAS_RELIABILITY_ROUTER = True
except ImportError:
    HAS_RELIABILITY_ROUTER = False

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
    description="""
Vendor Reliability Intelligence Platform API

Modules:
- User Authentication & Role Management
- Vendor Management
- Procurement Management
- Vendor Performance Management
- Vendor Reliability Management
- Contracts & Compliance
- Communications
- Notifications
- Reports
""".strip(),
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

if HAS_RELIABILITY_ROUTER:
    app.include_router(reliability.router, prefix=API_PREFIX)

app.include_router(contracts.router, prefix=API_PREFIX)
app.include_router(communications.router, prefix=API_PREFIX)
app.include_router(notifications.router, prefix=API_PREFIX)
app.include_router(reports.router, prefix=API_PREFIX)


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
            "reliability" if HAS_RELIABILITY_ROUTER else "reliability_not_configured",
            "contracts",
            "communications",
            "notifications",
            "reports",
        ],
    }


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "success",
        "message": "Backend is healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.API_VERSION,
    }