from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.core.database import get_db
from app.models.communication import Communication
from app.models.user import User
from app.schemas.communication import CommunicationCreate, CommunicationResponse

router = APIRouter(prefix="/communications", tags=["Communications"])


@router.post("/", response_model=CommunicationResponse)
def create_communication(
    payload: CommunicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    communication = Communication(**payload.dict())
    db.add(communication)
    db.commit()
    db.refresh(communication)
    return communication


@router.get("/", response_model=List[CommunicationResponse])
def list_communications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Communication).order_by(Communication.created_at.desc()).all()


@router.get("/{communication_id}", response_model=CommunicationResponse)
def get_communication(
    communication_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    communication = (
        db.query(Communication)
        .filter(Communication.id == communication_id)
        .first()
    )
    if not communication:
        raise HTTPException(status_code=404, detail="Communication not found")
    return communication
