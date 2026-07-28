from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    auth,
    contracts,
    notifications,
    performance,
    procurement,
    reliability,
    reports,
    vendors,
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

app.include_router(auth.router, tags=["Authentication"])
app.include_router(vendors.router, tags=["Vendors"])
app.include_router(procurement.router, tags=["Procurement"])
app.include_router(performance.router, tags=["Performance"])
app.include_router(contracts.router, tags=["Contracts"])
app.include_router(notifications.router, tags=["Notifications"])
app.include_router(reports.router, tags=["Reports"])
app.include_router(reliability.router, tags=["Reliability"])

@app.get("/")
def read_root():
    return {
        "message": "Vendor Reliability Intelligence Platform API",
        "status": "running",
    }

@app.get("/health")
def health_check():
    return {
        "status": "success",
        "message": "Backend is healthy",
    }