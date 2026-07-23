from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.contract import Contract
from app.schemas.contract import ContractCreate, ContractResponse

router = APIRouter(prefix="/contracts", tags=["Contracts"])


@router.post("/", response_model=ContractResponse)
def create_contract(payload: ContractCreate, db: Session = Depends(get_db)):
    contract = Contract(**payload.model_dump())
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return contract


@router.get("/", response_model=List[ContractResponse])
def list_contracts(db: Session = Depends(get_db)):
    return db.query(Contract).order_by(Contract.id.desc()).all()


@router.get("/expiring", response_model=List[ContractResponse])
def get_expiring_contracts(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    next_30_days = now + timedelta(days=30)

    return (
        db.query(Contract)
        .filter(Contract.end_date.isnot(None))
        .filter(Contract.end_date >= now)
        .filter(Contract.end_date <= next_30_days)
        .order_by(Contract.end_date.asc())
        .all()
    )


@router.get("/{contract_id}", response_model=ContractResponse)
def get_contract(contract_id: int, db: Session = Depends(get_db)):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract