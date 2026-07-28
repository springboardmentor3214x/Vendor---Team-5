from fastapi import APIRouter


router = APIRouter(prefix="/contracts", tags=["Contracts"])


@router.get("/")
def contracts_placeholder():
    return {
        "message": "Contracts API placeholder",
        "status": "ready",
    }
