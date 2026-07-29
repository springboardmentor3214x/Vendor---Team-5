from datetime import date

from app.services.purchase_order_service import (
    generate_purchase_order_number,
    calculate_total_cost,
    can_create_purchase_order,
    issue_purchase_order,
    mark_purchase_order_delivered,
    cancel_purchase_order,
    is_delivery_delayed,
    can_complete_procurement,
    can_complete_procurement_with_invoice_status,
    can_user_update_purchase_order
)
from app.utils.constants import (
    PROCUREMENT_REQUEST_STATUS_APPROVED,
    PURCHASE_ORDER_STATUS_CANCELLED,
    PURCHASE_ORDER_STATUS_DELIVERED,
    PURCHASE_ORDER_STATUS_DRAFT,
    PURCHASE_ORDER_STATUS_ISSUED
)
import pytest


def test_generate_purchase_order_number():
    assert generate_purchase_order_number(1) == "PO-2026-0001"


def test_calculate_total_cost():
    assert calculate_total_cost(10, 100, 180) == 1180


def test_can_create_purchase_order():
    assert can_create_purchase_order(PROCUREMENT_REQUEST_STATUS_APPROVED, True) is True


def test_cannot_create_purchase_order_without_vendor():
    assert can_create_purchase_order(PROCUREMENT_REQUEST_STATUS_APPROVED, False) is False


def test_issue_draft_purchase_order():
    assert issue_purchase_order(PURCHASE_ORDER_STATUS_DRAFT) == PURCHASE_ORDER_STATUS_ISSUED


def test_mark_issued_purchase_order_delivered():
    assert mark_purchase_order_delivered(PURCHASE_ORDER_STATUS_ISSUED) == (
        PURCHASE_ORDER_STATUS_DELIVERED
    )


def test_cancel_draft_purchase_order():
    assert cancel_purchase_order(PURCHASE_ORDER_STATUS_DRAFT) == (
        PURCHASE_ORDER_STATUS_CANCELLED
    )


def test_delivery_delayed():
    assert is_delivery_delayed(date(2026, 1, 1), date(2026, 1, 5)) is True


def test_can_complete_procurement_after_delivery_and_invoice_verification():
    assert can_complete_procurement(PURCHASE_ORDER_STATUS_DELIVERED, "verified") is True


@pytest.mark.parametrize(
    "invoice_status",
    ["verified", "approved", "paid", "Verified", "Approved", "Paid"],
)
def test_can_complete_procurement_with_eligible_invoice_status(invoice_status):
    assert can_complete_procurement_with_invoice_status(
        PURCHASE_ORDER_STATUS_DELIVERED, invoice_status
    ) is True


def test_completed_purchase_order_can_complete_procurement():
    assert can_complete_procurement_with_invoice_status("Completed", "paid") is True


@pytest.mark.parametrize("invoice_status", ["pending", "rejected"])
def test_ineligible_invoice_status_cannot_complete_procurement(invoice_status):
    assert can_complete_procurement_with_invoice_status(
        PURCHASE_ORDER_STATUS_DELIVERED, invoice_status
    ) is False


@pytest.mark.parametrize(
    ("po_status", "invoice_status", "expected"),
    [
        ("Delivered", "Verified", True),
        ("Delivered", "Approved", True),
        ("Delivered", "Paid", True),
        ("Completed", "Verified", True),
        ("Completed", "Approved", True),
        ("Completed", "Paid", True),
        ("Issued", "Paid", False),
        ("Cancelled", "Verified", False),
        ("Delivered", "Pending", False),
        ("Completed", "Rejected", False),
    ],
)
def test_procurement_completion_requires_eligible_purchase_order_and_invoice_status(
    po_status,
    invoice_status,
    expected,
):
    assert can_complete_procurement(po_status, invoice_status) is expected


def test_procurement_manager_can_update_purchase_order():
    assert can_user_update_purchase_order("Procurement Manager") is True


@pytest.mark.parametrize("sequence_number", [0, -1, True, 1.5])
def test_purchase_order_number_requires_positive_integer_sequence(sequence_number):
    with pytest.raises(ValueError, match="positive integer"):
        generate_purchase_order_number(sequence_number)


def test_expected_delivery_date_is_required():
    with pytest.raises(ValueError, match="Expected delivery date is required"):
        is_delivery_delayed(None, date(2026, 1, 5))
