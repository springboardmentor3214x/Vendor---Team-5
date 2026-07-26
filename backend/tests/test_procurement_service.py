from datetime import date

from app.services.procurement_service import (
    generate_procurement_request_number,
    approve_procurement_request,
    reject_procurement_request,
    cancel_procurement_request,
    can_send_back_procurement_request,
    can_edit_sent_back_request,
    resubmit_procurement_request,
    can_assign_vendor_to_request,
    can_user_manage_procurement_request
)
from app.utils.constants import (
    PROCUREMENT_REQUEST_STATUS_APPROVED,
    PROCUREMENT_REQUEST_STATUS_CANCELLED,
    PROCUREMENT_REQUEST_STATUS_PENDING,
    PROCUREMENT_REQUEST_STATUS_REJECTED
)
import pytest


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


@pytest.mark.parametrize("current_status", ["Pending", "Approved"])
def test_pending_or_approved_request_can_be_sent_back(current_status):
    assert can_send_back_procurement_request(current_status) is True


@pytest.mark.parametrize("current_status", ["Rejected", "Cancelled"])
def test_rejected_or_cancelled_request_cannot_be_sent_back(current_status):
    assert can_send_back_procurement_request(current_status) is False


def test_only_sent_back_request_can_be_edited_and_resubmitted():
    assert can_edit_sent_back_request("Sent Back") is True
    assert resubmit_procurement_request("Sent Back") == PROCUREMENT_REQUEST_STATUS_PENDING


@pytest.mark.parametrize("current_status", ["Pending", "Approved", "Rejected", "Cancelled"])
def test_only_sent_back_request_can_be_resubmitted(current_status):
    assert can_edit_sent_back_request(current_status) is False
    with pytest.raises(ValueError, match="Only sent-back"):
        resubmit_procurement_request(current_status)


@pytest.mark.parametrize("sequence_number", [0, -1, True, 1.5])
def test_procurement_request_number_requires_positive_integer_sequence(sequence_number):
    with pytest.raises(ValueError, match="positive integer"):
        generate_procurement_request_number(sequence_number)
