from fastapi import APIRouter


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/")
def auth_placeholder():
    return {
        "message": "Auth API placeholder",
        "status": "ready",
    }
