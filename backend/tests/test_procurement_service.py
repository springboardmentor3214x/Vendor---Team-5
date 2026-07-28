from datetime import date

from app.services.procurement_service import (
    generate_procurement_request_number,
    approve_procurement_request,
    reject_procurement_request,
    cancel_procurement_request,
    can_assign_vendor_to_request,
    can_user_manage_procurement_request
)
from app.utils.constants import (
    PROCUREMENT_REQUEST_STATUS_APPROVED,
    PROCUREMENT_REQUEST_STATUS_CANCELLED,
    PROCUREMENT_REQUEST_STATUS_PENDING,
    PROCUREMENT_REQUEST_STATUS_REJECTED
)


def test_generate_procurement_request_number():
    assert generate_procurement_request_number(1) == "PR-2026-0001"


def test_can_assign_vendor_after_approval():
    assert can_assign_vendor_to_request(PROCUREMENT_REQUEST_STATUS_APPROVED) is True


def test_cannot_assign_vendor_before_approval():
    assert can_assign_vendor_to_request(PROCUREMENT_REQUEST_STATUS_PENDING) is False


def test_approve_pending_procurement_request():
    assert approve_procurement_request(PROCUREMENT_REQUEST_STATUS_PENDING) == (
        PROCUREMENT_REQUEST_STATUS_APPROVED
    )


def test_reject_pending_procurement_request():
    assert reject_procurement_request(PROCUREMENT_REQUEST_STATUS_PENDING) == (
        PROCUREMENT_REQUEST_STATUS_REJECTED
    )


def test_cancel_approved_procurement_request():
    assert cancel_procurement_request(PROCUREMENT_REQUEST_STATUS_APPROVED) == (
        PROCUREMENT_REQUEST_STATUS_CANCELLED
    )


def test_procurement_manager_can_manage_procurement_request():
    assert can_user_manage_procurement_request("Procurement Manager") is True
