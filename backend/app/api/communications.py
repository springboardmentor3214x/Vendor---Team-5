from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.communication import Communication
from app.schemas.communication import CommunicationCreate, CommunicationResponse

router = APIRouter(prefix="/communications", tags=["Communications"])


@router.post("/", response_model=CommunicationResponse)
def create_communication(payload: CommunicationCreate, db: Session = Depends(get_db)):
    communication = Communication(**payload.dict())
    db.add(communication)
    db.commit()
    db.refresh(communication)
    return communication


@router.get("/", response_model=List[CommunicationResponse])
def list_communications(db: Session = Depends(get_db)):
    return db.query(Communication).order_by(Communication.created_at.desc()).all()


@router.get("/{communication_id}", response_model=CommunicationResponse)
def get_communication(communication_id: int, db: Session = Depends(get_db)):
    communication = (
        db.query(Communication)
        .filter(Communication.id == communication_id)
        .first()
    )
    if not communication:
        raise HTTPException(status_code=404, detail="Communication not found")
    return communication