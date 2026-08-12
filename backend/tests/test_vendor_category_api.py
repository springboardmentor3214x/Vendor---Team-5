import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from types import SimpleNamespace

from app.api.auth import get_current_user
from app.api.vendors import create_vendor, list_vendor_categories, update_vendor
from app.core.database import get_db
from app.core.security import create_access_token
from app.main import app
from app.models.user import User
from app.models.vendor import Vendor
from app.schemas.vendor import VendorCreate, VendorUpdate


class Category:
    def __init__(self, category_id, name):
        self.id = category_id
        self.name = name
        self.description = "Test category"
        self.is_active = True


class Query:
    def __init__(self, values):
        self.values = values
        self.predicate = None

    def filter(self, predicate):
        self.predicate = predicate
        return self

    def order_by(self, _field):
        return self

    def first(self):
        if self.predicate is None:
            return self.values[0] if self.values else None
        field = self.predicate.left.key
        value = self.predicate.right.value
        return next((item for item in self.values if getattr(item, field) == value), None)

    def all(self):
        return self.values


class Db:
    def __init__(self):
        self.categories = [Category(7, "IT Vendors")]
        self.vendors = []

    def query(self, model):
        return Query(self.categories if model.__name__ == "VendorCategory" else self.vendors)

    def add(self, vendor):
        vendor.id = len(self.vendors) + 1
        self.vendors.append(vendor)

    def commit(self):
        pass

    def refresh(self, _item):
        pass


def payload(**overrides):
    return VendorCreate.model_validate({
        "companyName": "Acme", "contactPersonName": "Ada", "email": "ada@acme.example",
        "phoneNumber": "1234567890", **overrides,
    })


def test_create_vendor_with_category_id():
    db = Db()
    vendor = create_vendor(payload(categoryId=7), db)
    assert vendor.category_id == 7


def test_create_vendor_with_category_label_does_not_pass_label_to_model():
    db = Db()
    vendor = create_vendor(payload(vendorCategory="IT Vendors"), db)
    assert vendor.category_id == 7
    assert not hasattr(vendor, "vendor_category")


def test_create_vendor_with_invalid_category_label_returns_400():
    with pytest.raises(HTTPException, match="Invalid vendor category") as exc:
        create_vendor(payload(vendorCategory="Unknown"), Db())
    assert exc.value.status_code == 400


def test_update_vendor_category_label_updates_category_id():
    db = Db()
    vendor = create_vendor(payload(categoryId=7), db)
    updated = update_vendor(1, VendorUpdate.model_validate({"vendorCategory": "IT Vendors"}), db)
    assert updated.category_id == 7


def test_category_list_returns_id_and_name():
    categories = list_vendor_categories(Db())
    assert [(category.id, category.name) for category in categories] == [(7, "IT Vendors")]


class AccessQuery(Query):
    """Small SQLAlchemy-query double for authenticated vendor route checks."""


class AccessDb:
    def __init__(self):
        self.vendor_a = SimpleNamespace(id=1, email="vendor-a@example.test")
        self.vendor_b = SimpleNamespace(id=2, email="vendor-b@example.test")
        self.user_a = SimpleNamespace(
            id=101,
            email="vendor-a@example.test",
            role="Vendor",
            is_active=True,
        )

    def query(self, model):
        if model is User:
            return AccessQuery([self.user_a])
        if model is Vendor:
            return AccessQuery([self.vendor_a, self.vendor_b])
        return AccessQuery([])


def test_vendor_a_token_cannot_read_vendor_b_detail_or_documents():
    """A valid Vendor JWT must not grant record-level access to another vendor."""
    db = AccessDb()
    app.dependency_overrides[get_db] = lambda: db
    try:
        token = create_access_token({"sub": db.user_a.email, "role": "Vendor", "user_id": db.user_a.id})
        headers = {"Authorization": f"Bearer {token}"}
        with TestClient(app) as client:
            detail = client.get("/vendors/2", headers=headers)
            documents = client.get("/vendors/2/documents", headers=headers)

        assert detail.status_code == 403, detail.text
        assert documents.status_code == 403, documents.text
    finally:
        app.dependency_overrides.clear()


@pytest.mark.parametrize(
    ("filename", "contents", "expected_status"),
    [
        ("not-allowed.exe", b"x", 415),
        ("too-large.pdf", b"x" * (10 * 1024 * 1024 + 1), 413),
    ],
    ids=["disallowed_type", "oversized_file"],
)
def test_vendor_document_upload_enforces_type_and_size_limits(filename, contents, expected_status):
    db = AccessDb()
    admin = SimpleNamespace(id=1, email="admin@example.test", role="Administrator", is_active=True)
    app.dependency_overrides[get_current_user] = lambda: admin
    app.dependency_overrides[get_db] = lambda: db
    try:
        with TestClient(app) as client:
            response = client.post(
                "/vendors/1/documents",
                data={"document_type": "Supporting document"},
                files={"file": (filename, contents, "application/octet-stream")},
            )
        assert response.status_code == expected_status, response.text
    finally:
        app.dependency_overrides.clear()
