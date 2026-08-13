import os
import pytest
from datetime import datetime
from app.core.database import SessionLocal
from app.core.security import verify_password
from app.models.user import User
from app.models.role import Role
from app.models.vendor import Vendor
from app.models.vendor_document import VendorDocument
from app.models.contract_document import ContractDocument
from app.models.procurement_request import ProcurementRequest
from app.models.procurement_request_document import ProcurementRequestDocument
from app.models.invoice import Invoice
from app.models.invoice_document import InvoiceDocument
from app.models.vendor_issue import VendorIssue


def test_demo_account_bcrypt_passwords_for_all_seeded_roles():
    """Verify that all 7 demo accounts exist and can authenticate using BCrypt hash of Demo@123."""
    db = SessionLocal()
    try:
        demo_emails = [
            "admin@vendoriq.com",
            "pm.manager@vendoriq.com",
            "scm.manager@vendoriq.com",
            "vendor.contact@samplesupplies.com",
            "finance.officer@vendoriq.com",
            "auditor@vendoriq.com",
            "dept.user@vendoriq.com",
        ]
        for email in demo_emails:
            user = db.query(User).filter(User.email == email).first()
            assert user is not None, f"Demo user account {email} should exist in database."
            assert user.hashed_password != "placeholder_hash", f"Demo user {email} should not hold placeholder_hash."
            assert verify_password("Demo@123", user.hashed_password), f"Demo user {email} password verification failed."
            assert user.role in [
                "Administrator",
                "Procurement Manager",
                "Supply Chain Manager",
                "Vendor",
                "Finance Officer",
                "Auditor",
                "Department User",
            ], f"User {email} has role {user.role}."
    finally:
        db.close()


def test_vendor_and_contract_document_lifecycle_fields():
    """Verify versioning, replacement tracking, and physical file existence for vendor & contract documents."""
    db = SessionLocal()
    try:
        # Vendor Documents
        v2_doc = db.query(VendorDocument).filter(VendorDocument.file_name == "gst_cert_sample_v2.pdf").first()
        assert v2_doc is not None
        assert v2_doc.version == 2
        assert v2_doc.is_current is True
        assert v2_doc.replaced_document_id is not None
        v1_doc = db.query(VendorDocument).filter(VendorDocument.id == v2_doc.replaced_document_id).first()
        assert v1_doc is not None
        assert v1_doc.version == 1
        assert v1_doc.is_current is False
        assert os.path.exists(v2_doc.file_path)

        # Contract Documents
        cd_v2 = db.query(ContractDocument).filter(ContractDocument.file_name == "steel_master_agreement_signed_v2.pdf").first()
        assert cd_v2 is not None
        assert cd_v2.version == 2
        assert cd_v2.is_current is True
        assert cd_v2.replaced_document_id is not None
        assert cd_v2.content_type == "application/pdf"
        assert cd_v2.uploaded_by is not None
        assert os.path.exists(cd_v2.file_path)
    finally:
        db.close()


def test_procurement_request_document_model_and_draft_status():
    """Verify ProcurementRequestDocument schema, replacement tracking, and Draft request support."""
    db = SessionLocal()
    try:
        # Draft Procurement Request
        draft_req = db.query(ProcurementRequest).filter(ProcurementRequest.request_number == "REQ-2026-006").first()
        assert draft_req is not None
        assert draft_req.approval_status == "Draft"

        # Procurement Request Document replacement
        prd_v2 = db.query(ProcurementRequestDocument).filter(ProcurementRequestDocument.file_name == "steel_spec_v2.pdf").first()
        assert prd_v2 is not None
        assert prd_v2.version == 2
        assert prd_v2.is_current is True
        assert prd_v2.replaced_document_id is not None
        assert os.path.exists(prd_v2.file_path)
    finally:
        db.close()


def test_invoice_document_model_and_backward_compatibility():
    """Verify InvoiceDocument schema and backward compatibility of Invoice supporting_document_url."""
    db = SessionLocal()
    try:
        inv = db.query(Invoice).filter(Invoice.invoice_number == "INV-2026-001").first()
        assert inv is not None
        assert inv.supporting_document_url is not None

        inv_doc_v2 = db.query(InvoiceDocument).filter(InvoiceDocument.file_name == "inv_2026_001_v2.pdf").first()
        assert inv_doc_v2 is not None
        assert inv_doc_v2.invoice_id == inv.id
        assert inv_doc_v2.version == 2
        assert inv_doc_v2.is_current is True
        assert inv_doc_v2.replaced_document_id is not None
        assert os.path.exists(inv_doc_v2.file_path)
    finally:
        db.close()


def test_vendor_issue_complaint_and_resolution_tracking():
    """Verify VendorIssue model CRUD, categories, severity, status, and resolution fields."""
    db = SessionLocal()
    try:
        issues = db.query(VendorIssue).all()
        assert len(issues) >= 3

        open_issue = db.query(VendorIssue).filter(VendorIssue.status == "Open").first()
        assert open_issue is not None
        assert open_issue.issue_category == "Quality Defect"
        assert open_issue.severity == "High"

        resolved_issue = db.query(VendorIssue).filter(VendorIssue.status == "Resolved").first()
        assert resolved_issue is not None
        assert resolved_issue.resolution_notes is not None
        assert resolved_issue.resolved_by is not None
        assert resolved_issue.resolved_date is not None
    finally:
        db.close()
