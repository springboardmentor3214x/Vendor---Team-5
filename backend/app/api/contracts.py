from typing import List
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.api.auth import get_current_user
from app.schemas.contract import (
    ContractCreate,
    ContractUpdate,
    ContractResponse,
    ContractRenewalCreate,
    ContractRenewalOut
)
from app.services import contract_service
from app.services.reliability_service import recalculate_vendor_reliability

router = APIRouter(prefix="/contracts", tags=["Contracts"])


@router.post("/", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
def create_contract(payload: ContractCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Role-Based Access: Admin or Procurement Manager can create contracts
    if current_user.role.name not in ["Administrator", "Procurement Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Administrators or Procurement Managers can create contracts"
        )
    
    contract = contract_service.create_contract(db, payload)
    try:
        recalculate_vendor_reliability(contract.vendor_id, db)
    except Exception as e:
        print(f"Error recalculating reliability for vendor {contract.vendor_id}: {e}")
    return contract


@router.get("/", response_model=List[ContractResponse])
def list_contracts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Role-Based Access: Vendors see only their contracts. Admins/Managers/Finance/Auditor see all.
    if current_user.role.name == "Vendor":
        # Find vendor by matching user email
        from app.models.vendor import Vendor
        vendor = db.query(Vendor).filter(Vendor.email == current_user.email).first()
        if not vendor:
            return []
        return db.query(contract_service.Contract).filter(contract_service.Contract.vendor_id == vendor.id).all()
        
    return contract_service.list_contracts(db)


@router.get("/expiring", response_model=List[ContractResponse])
def get_expiring_contracts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role.name not in ["Administrator", "Procurement Manager", "Supply Chain Manager", "Auditor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    return contract_service.get_expiring_contracts(db)


@router.get("/{contract_id}", response_model=ContractResponse)
def get_contract(contract_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    contract = contract_service.get_contract(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
        
    # Vendor restriction
    if current_user.role.name == "Vendor":
        from app.models.vendor import Vendor
        vendor = db.query(Vendor).filter(Vendor.email == current_user.email).first()
        if not vendor or contract.vendor_id != vendor.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
            
    return contract


@router.patch("/{contract_id}", response_model=ContractResponse)
def update_contract(contract_id: int, payload: ContractUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role.name not in ["Administrator", "Procurement Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Administrators or Procurement Managers can update contracts"
        )
        
    contract = contract_service.update_contract(db, contract_id, payload)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
        
    try:
        recalculate_vendor_reliability(contract.vendor_id, db)
    except Exception as e:
        print(f"Error recalculating reliability for vendor {contract.vendor_id}: {e}")
        
    return contract


@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contract(contract_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role.name not in ["Administrator"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Administrators can delete contracts"
        )
        
    contract = contract_service.get_contract(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
        
    contract_service.delete_contract(db, contract_id)
    try:
        recalculate_vendor_reliability(contract.vendor_id, db)
    except Exception as e:
        print(f"Error recalculating reliability for vendor {contract.vendor_id}: {e}")


@router.post("/{contract_id}/renew", response_model=ContractResponse)
def renew_contract(contract_id: int, payload: ContractRenewalCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role.name not in ["Administrator", "Procurement Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Administrators or Procurement Managers can renew contracts"
        )
        
    contract = contract_service.renew_contract(db, contract_id, payload)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
        
    try:
        recalculate_vendor_reliability(contract.vendor_id, db)
    except Exception as e:
        print(f"Error recalculating reliability for vendor {contract.vendor_id}: {e}")
        
    return contract


@router.patch("/{contract_id}/status", response_model=ContractResponse)
def update_contract_status(contract_id: int, status_str: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role.name not in ["Administrator", "Procurement Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
        
    contract = contract_service.update_contract_status(db, contract_id, status_str)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
        
    try:
        recalculate_vendor_reliability(contract.vendor_id, db)
    except Exception as e:
        print(f"Error recalculating reliability for vendor {contract.vendor_id}: {e}")
        
    return contract