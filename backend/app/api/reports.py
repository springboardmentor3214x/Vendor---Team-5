from fastapi import APIRouter


router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/")
def reports_placeholder():
    return {
        "message": "Reports API placeholder",
        "status": "ready",
    }
