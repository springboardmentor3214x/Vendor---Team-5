import pytest
from fastapi import HTTPException

from app.api.vendors import create_vendor, list_vendor_categories, update_vendor
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
