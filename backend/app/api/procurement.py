from fastapi import APIRouter


router = APIRouter(prefix="/procurement", tags=["Procurement"])


@router.get("/")
def procurement_placeholder():
    return {
        "message": "Procurement API placeholder",
        "status": "ready",
    }
