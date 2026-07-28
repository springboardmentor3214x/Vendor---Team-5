from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional

from app.models.contract import Contract
from app.models.contract_renewal import ContractRenewal
from app.schemas.contract import ContractCreate, ContractUpdate, ContractRenewalCreate


def create_contract(db: Session, payload: ContractCreate) -> Contract:
    contract = Contract(**payload.model_dump())
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return contract


def get_contract(db: Session, contract_id: int) -> Optional[Contract]:
    return db.query(Contract).filter(Contract.id == contract_id).first()


def list_contracts(db: Session) -> List[Contract]:
    return db.query(Contract).all()


def update_contract(db: Session, contract_id: int, payload: ContractUpdate) -> Optional[Contract]:
    contract = get_contract(db, contract_id)
    if not contract:
        return None
    
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(contract, key, value)
        
    db.commit()
    db.refresh(contract)
    return contract


def delete_contract(db: Session, contract_id: int) -> bool:
    contract = get_contract(db, contract_id)
    if not contract:
        return False
    db.delete(contract)
    db.commit()
    return True


def renew_contract(db: Session, contract_id: int, payload: ContractRenewalCreate) -> Optional[Contract]:
    contract = get_contract(db, contract_id)
    if not contract:
        return None

    # Calculate new value
    new_value = payload.renewal_value if payload.renewal_value else contract.contract_value

    # Create Contract Renewal history record
    renewal = ContractRenewal(
        contract_id=contract.id,
        renewal_date=datetime.utcnow(),
        new_end_date=payload.new_end_date,
        renewal_value=new_value,
        remarks=payload.remarks
    )
    db.add(renewal)

    # Update Contract model
    contract.end_date = payload.new_end_date
    contract.contract_value = new_value
    contract.status = "Renewed"
    contract.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(contract)
    return contract


def get_expiring_contracts(db: Session) -> List[Contract]:
    # Query active/renewed/draft contracts nearing expiration
    now = datetime.utcnow()
    # Expiring in 90, 30, 7 days or today
    exp_90 = now + timedelta(days=90)
    exp_30 = now + timedelta(days=30)
    exp_7 = now + timedelta(days=7)
    
    # Let's filter contracts whose end_date is between today and 90 days from now
    return db.query(Contract).filter(
        Contract.status.in_(["Active", "Renewed", "Draft"]),
        Contract.end_date >= now,
        Contract.end_date <= exp_90
    ).all()


def update_contract_status(db: Session, contract_id: int, status: str) -> Optional[Contract]:
    contract = get_contract(db, contract_id)
    if not contract:
        return None
    contract.status = status
    contract.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(contract)
    return contract
