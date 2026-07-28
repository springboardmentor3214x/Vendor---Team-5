from typing import List
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.contract import Contract
from app.schemas.contract import ContractCreate, ContractResponse
from app.services.reliability_service import recalculate_vendor_reliability

router = APIRouter(prefix="/contracts", tags=["Contracts"])


@router.post("/", response_model=ContractResponse)
def create_contract(payload: ContractCreate, db: Session = Depends(get_db)):
    contract = Contract(**payload.dict())
    db.add(contract)
    db.commit()
    db.refresh(contract)
    try:
        recalculate_vendor_reliability(contract.vendor_id, db)
    except Exception as e:
        print(f"Error recalculating reliability for vendor {contract.vendor_id}: {e}")
    return contract


@router.get("/", response_model=List[ContractResponse])
def list_contracts(db: Session = Depends(get_db)):
    return db.query(Contract).all()


@router.get("/expiring", response_model=List[ContractResponse])
def get_expiring_contracts(db: Session = Depends(get_db)):
    today = datetime.utcnow()
    next_30_days = today + timedelta(days=30)
    return (
        db.query(Contract)
        .filter(Contract.end_date.isnot(None))
        .filter(Contract.end_date <= next_30_days)
        .all()
    )


@router.get("/{contract_id}", response_model=ContractResponse)
def get_contract(contract_id: int, db: Session = Depends(get_db)):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract