from unittest.mock import MagicMock
from datetime import datetime, timedelta
import pytest

from app.services import contract_service, compliance_service, certification_service
from app.models.contract import Contract
from app.models.certification import Certification
from app.models.compliance import ComplianceRecord
from app.schemas.contract import ContractCreate, ContractUpdate, ContractRenewalCreate
from app.schemas.compliance import ComplianceRecordCreate
from app.schemas.certification import CertificationCreate, CertificationUpdate


def test_create_contract():
    db = MagicMock()
    payload = ContractCreate(
        vendor_id=1,
        contract_number="CON-TEST-101",
        contract_title="Test Agreement",
        contract_type="NDA",
        procurement_category="IT",
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=30),
        contract_value=10000.0,
        payment_terms="Net 15",
        sla="Response within 2h",
        warranty_details="No warranty",
        responsible_manager="John Doe",
        status="Draft",
        compliance_verified=False
    )

    contract = contract_service.create_contract(db, payload)
    
    assert contract is not None
    assert contract.contract_number == "CON-TEST-101"
    assert contract.contract_title == "Test Agreement"
    db.add.assert_called_once()
    db.commit.assert_called_once()


def test_renew_contract():
    db = MagicMock()
    # Fake initial contract
    initial_contract = Contract(
        id=1,
        vendor_id=1,
        contract_number="CON-TEST-101",
        contract_title="Test Agreement",
        end_date=datetime.utcnow(),
        contract_value=5000.0,
        status="Active"
    )
    
    db.query.return_value.filter.return_value.first.return_value = initial_contract
    
    new_end = datetime.utcnow() + timedelta(days=365)
    payload = ContractRenewalCreate(
        new_end_date=new_end,
        renewal_value=6000.0,
        remarks="Extending for 1 year"
    )

    updated_contract = contract_service.renew_contract(db, contract_id=1, payload=payload)
    
    assert updated_contract is not None
    assert updated_contract.end_date == new_end
    assert updated_contract.contract_value == 6000.0
    assert updated_contract.status == "Renewed"
    db.commit.assert_called_once()


def test_create_compliance_record():
    db = MagicMock()
    payload = ComplianceRecordCreate(
        vendor_id=1,
        compliance_type="Safety Regulations",
        status="Pending Verification",
        remarks="Awaiting site safety audit report"
    )

    record = compliance_service.create_compliance_record(db, payload)
    
    assert record is not None
    assert record.compliance_type == "Safety Regulations"
    assert record.status == "Pending Verification"
    db.add.assert_called_once()
    db.commit.assert_called_once()


def test_verify_compliance():
    db = MagicMock()
    initial_record = ComplianceRecord(
        id=1,
        vendor_id=1,
        compliance_type="Safety Regulations",
        status="Pending Verification"
    )
    db.query.return_value.filter.return_value.first.return_value = initial_record
    
    verified_record = compliance_service.verify_compliance(
        db,
        compliance_id=1,
        status="Compliant",
        verified_by=2,
        remarks="Audit completed successfully"
    )
    
    assert verified_record is not None
    assert verified_record.status == "Compliant"
    assert verified_record.verified_by == 2
    assert verified_record.remarks == "Audit completed successfully"
    db.commit.assert_called_once()


def test_add_certification():
    db = MagicMock()
    payload = CertificationCreate(
        vendor_id=1,
        certification_name="ISO 27001",
        certificate_number="ISO27001-9872",
        issuing_authority="BSI",
        issue_date=datetime.utcnow() - timedelta(days=10),
        expiry_date=datetime.utcnow() + timedelta(days=355),
        document_url="uploads/iso27001.pdf"
    )
    
    cert = certification_service.add_certification(db, payload)
    
    assert cert is not None
    assert cert.certification_name == "ISO 27001"
    assert cert.certificate_number == "ISO27001-9872"
    db.add.assert_called_once()
    db.commit.assert_called_once()
