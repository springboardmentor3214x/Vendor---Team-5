from datetime import date

from app.services.procurement_service import (
    generate_procurement_request_number,
    can_assign_vendor_to_request,
    can_complete_procurement,
    is_delivery_delayed,
    can_user_update_procurement_status
)


def test_generate_procurement_request_number():
    assert generate_procurement_request_number(1) == "PR-2026-0001"


def test_can_assign_vendor_after_approval():
    assert can_assign_vendor_to_request("approved") is True


def test_cannot_assign_vendor_before_approval():
    assert can_assign_vendor_to_request("pending") is False


def test_can_complete_procurement_after_delivery_and_invoice_verification():
    assert can_complete_procurement("delivered", True) is True


def test_delivery_delayed():
    assert is_delivery_delayed(
        expected_delivery_date=date(2026, 1, 1),
        actual_delivery_date=date(2026, 1, 5)
    ) is True


def test_procurement_manager_can_update_status():
    assert can_user_update_procurement_status("Procurement Manager") is True