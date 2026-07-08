from fastapi import APIRouter


router = APIRouter(prefix="/vendors", tags=["Vendors"])


@router.get("/")
def vendors_placeholder():
    return {
        "message": "Vendors API placeholder",
        "status": "ready",
    }
