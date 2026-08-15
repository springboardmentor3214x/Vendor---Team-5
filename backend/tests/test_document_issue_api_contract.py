"""Focused API-layer coverage for the document, PO print, and issue endpoints."""

import asyncio
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.api import contracts, documents, performance, procurement
from app.api.file_storage import StoredUpload
from app.main import app
from app.models.procurement_request import ProcurementRequest
from app.models.purchase_order import PurchaseOrder
from app.models.vendor import Vendor
from app.schemas.document_lifecycle import VendorIssueCreate


class _Query:
    def __init__(self, result=None, rows=None):
        self.result = result
        self.rows = rows if rows is not None else ([] if result is None else [result])

    def filter(self, *_conditions):
        return self

    def order_by(self, *_values):
        return self

    def first(self):
        return self.result

    def all(self):
        return self.rows


class _Db:
    def __init__(self, mapping):
        self.mapping = mapping

    def query(self, model):
        value = self.mapping.get(model)
        return _Query(value, value if isinstance(value, list) else None)


def _admin():
    return SimpleNamespace(id=9, email="admin@example.test", role="Administrator")


def _document(**overrides):
    values = {
        "id": 4,
        "document_type": "Supporting Document",
        "file_name": "scope.pdf",
        "file_path": "C:/uploads/scope.pdf",
        "file_size": 12,
        "content_type": "application/pdf",
        "uploaded_by": 9,
        "uploaded_at": None,
        "version": 1,
        "is_current": True,
        "replaced_document_id": None,
        "replaced_at": None,
        "replaced_by": None,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_new_api_routes_are_registered_and_jwt_protected():
    paths = app.openapi()["paths"]
    expected = {
        "/procurement/procurement-requests/{request_id}/documents",
        "/procurement/invoices/{invoice_id}/documents",
        "/contracts/{contract_id}/documents",
        "/documents/{document_id}/replace",
        "/procurement/purchase-orders/{po_id}/print",
        "/performance/vendors/{vendor_id}/issues",
    }
    assert expected <= set(paths)

    with TestClient(app) as client:
        response = client.get("/procurement/procurement-requests/1/documents")
    assert response.status_code == 401


def test_request_document_upload_uses_procurement_document_service(monkeypatch):
    request = SimpleNamespace(id=7, requested_by=9)
    db = _Db({ProcurementRequest: request})
    uploaded = _document(request_id=7)
    captured = {}

    async def fake_store(_file, *, area):
        assert area == "procurement_request_documents"
        return StoredUpload("scope.pdf", "C:/uploads/scope.pdf", 12, "application/pdf")

    def fake_create(_db, **metadata):
        captured.update(metadata)
        return uploaded

    monkeypatch.setattr(procurement, "store_document_upload", fake_store)
    monkeypatch.setattr(
        procurement.procurement_document_service,
        "create_procurement_request_document",
        fake_create,
    )

    result = asyncio.run(
        procurement.upload_request_document(
            7, "Scope", None, _admin(), db
        )
    )
    assert captured["request_id"] == 7
    assert captured["uploaded_by"] == 9
    assert result["document_type"] == "Supporting Document"


def test_vendor_document_replace_uses_versioning_service(monkeypatch):
    previous = _document(vendor_id=3)
    replacement = _document(id=5, vendor_id=3, version=2, replaced_document_id=4)
    captured = {}

    async def fake_store(_file, *, area):
        assert area == "vendor_documents"
        return StoredUpload("scope-v2.pdf", "C:/uploads/scope-v2.pdf", 15, "application/pdf")

    def fake_replace(_db, _document_id, **metadata):
        captured.update(metadata)
        return replacement

    monkeypatch.setattr(documents.document_service, "get_document_by_id", lambda *_: previous)
    monkeypatch.setattr(documents, "store_document_upload", fake_store)
    monkeypatch.setattr(documents.document_service, "replace_vendor_document", fake_replace)
    monkeypatch.setattr(documents, "refresh_after_compliance_update", lambda *_: None)

    result = asyncio.run(documents.replace_vendor_document(4, "GST Certificate", None, _Db({}), _admin()))
    assert captured["uploaded_by"] == 9
    assert result.id == 5
    assert result.version == 2


def test_purchase_order_print_returns_real_pdf():
    po = SimpleNamespace(
        id=4,
        procurement_request_id=7,
        vendor_id=3,
        po_number="PO-2026-0004",
        po_status="Issued",
        quantity=2,
        unit_price=50,
        total_cost=100,
        tax_details=0,
        shipping_address=None,
        expected_delivery_date=None,
        actual_delivery_date=None,
        payment_terms="Net 30",
        project_name=None,
    )
    request = SimpleNamespace(
        id=7,
        request_number="REQ-2026-0007",
        title="Steel",
        department="Operations",
        project_name=None,
        item_description="Steel sheets",
        product_name="Steel",
        product_category="Materials",
        quantity=2,
        unit_of_measurement="pcs",
        business_justification="Project need",
        required_delivery_date=None,
    )
    vendor = SimpleNamespace(
        id=3,
        company_name="Acme",
        contact_person_name="Asha",
        email=None,
        phone_number=None,
        address_line1=None,
        address_line2=None,
        city=None,
        state=None,
        country=None,
        pincode=None,
        gst_number=None,
        pan_number=None,
    )
    db = _Db({PurchaseOrder: po, ProcurementRequest: request, Vendor: vendor})
    response = procurement.print_purchase_order(4, _admin(), db)
    assert response.media_type == "application/pdf"
    assert response.body.startswith(b"%PDF-")
    assert "PO-2026-0004.pdf" in response.headers["content-disposition"]


def test_issue_create_uses_issue_service_and_maps_category(monkeypatch):
    vendor = SimpleNamespace(id=3)
    issue = SimpleNamespace(
        id=6,
        vendor_id=3,
        purchase_order_id=None,
        issue_category="Late Delivery",
        severity="High",
        description="Supplier missed the committed date.",
        status="Open",
        reported_by=9,
        reported_date=None,
        assigned_to=None,
        resolution_notes=None,
        resolved_by=None,
        resolved_date=None,
        created_at=None,
        updated_at=None,
    )
    captured = {}

    def fake_create(_db, **values):
        captured.update(values)
        return issue

    monkeypatch.setattr(performance.vendor_issue_service, "create_vendor_issue", fake_create)
    result = performance.create_issue(
        3,
        VendorIssueCreate(category="Late Delivery", severity="High", description="Supplier missed the committed date."),
        _Db({Vendor: vendor}),
        _admin(),
    )
    assert captured["issue_category"] == "Late Delivery"
    assert result["category"] == "Late Delivery"
