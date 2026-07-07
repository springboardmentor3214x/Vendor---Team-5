from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    auth,
    contracts,
    notifications,
    performance,
    procurement,
    reports,
    vendors,
)
from app.core.config import settings


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(vendors.router)
app.include_router(procurement.router)
app.include_router(performance.router)
app.include_router(contracts.router)
app.include_router(notifications.router)
app.include_router(reports.router)


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
