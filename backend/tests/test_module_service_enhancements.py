from datetime import datetime

import pytest

from app.services import contract_document_service, document_service, vendor_issue_service
from app.services.purchase_order_service import render_purchase_order_pdf


class _Document:
    def __init__(self, document_id=1, parent_id=7, document_type="Agreement", version=1, is_current=True):
        self.id = document_id
        self.vendor_id = parent_id
        self.contract_id = parent_id
        self.document_type = document_type
        self.version = version
        self.is_current = is_current
        self.replaced_at = None
        self.replaced_by = None


class _Db:
    def __init__(self):
        self.added = []
        self.committed = False

    def add(self, value):
        self.added.append(value)

    def commit(self):
        self.committed = True

    def refresh(self, _value):
        pass


def test_vendor_replacement_keeps_the_prior_document(monkeypatch):
    old = _Document()
    db = _Db()
    monkeypatch.setattr(document_service, "get_document_by_id", lambda *_: old)

    replacement = document_service.replace_vendor_document(
        db, 1, file_name="agreement-v2.pdf", file_path="/files/agreement-v2.pdf", uploaded_by=9
    )

    assert old.is_current is False
    assert old.replaced_by == 9
    assert replacement.replaced_document_id == old.id
    assert replacement.version == 2
    assert replacement.is_current is True
    assert db.committed is True


def test_contract_replacement_rejects_a_historical_document(monkeypatch):
    old = _Document(is_current=False)
    monkeypatch.setattr(contract_document_service, "get_contract_document", lambda *_: old)

    with pytest.raises(ValueError, match="current document"):
        contract_document_service.replace_contract_document(
            _Db(), 1, file_name="agreement-v3.pdf", file_path="/files/agreement-v3.pdf"
        )


def test_resolving_an_issue_requires_notes_and_records_resolution(monkeypatch):
    class Issue:
        status = "Open"
        resolution_notes = None
        resolved_date = None
        resolved_by = None

    issue = Issue()
    db = _Db()
    monkeypatch.setattr(vendor_issue_service, "get_vendor_issue", lambda *_: issue)

    with pytest.raises(ValueError, match="Resolution notes"):
        vendor_issue_service.resolve_vendor_issue(db, 1, resolution_notes="", resolved_by=4)

    resolved = vendor_issue_service.resolve_vendor_issue(db, 1, resolution_notes="Vendor supplied replacement", resolved_by=4)
    assert resolved.status == "Resolved"
    assert resolved.resolved_by == 4
    assert isinstance(resolved.resolved_date, datetime)


def test_purchase_order_pdf_service_returns_a_pdf():
    po = type("PO", (), {"id": 1, "po_number": "PO-2026-0001", "po_status": "Issued", "quantity": 2,
                           "unit_price": 50, "total_cost": 100, "tax_details": None, "shipping_address": None,
                           "expected_delivery_date": None, "actual_delivery_date": None, "payment_terms": "Net 30", "project_name": None})()
    request = type("Request", (), {"id": 1, "request_number": "REQ-1", "title": "Steel", "department": "Ops",
                                     "project_name": None, "item_description": "Steel sheets", "product_name": "Steel",
                                     "product_category": "Materials", "quantity": 2, "unit_of_measurement": "pcs",
                                     "business_justification": "Project", "required_delivery_date": None})()
    vendor = type("Vendor", (), {"id": 1, "company_name": "Acme", "contact_person_name": "Asha", "email": None,
                                  "phone_number": None, "address_line1": None, "address_line2": None, "city": None,
                                  "state": None, "country": None, "pincode": None, "gst_number": None, "pan_number": None})()

    assert render_purchase_order_pdf(po, request, vendor).startswith(b"%PDF")
