from fastapi import APIRouter


router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/")
def notifications_placeholder():
    return {
        "message": "Notifications API placeholder",
        "status": "ready",
    }
