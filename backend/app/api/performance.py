from fastapi import APIRouter


router = APIRouter(prefix="/performance", tags=["Performance"])


@router.get("/")
def performance_placeholder():
    return {
        "message": "Performance API placeholder",
        "status": "ready",
    }
