from backend.app.utils.constants import (
    PROCUREMENT_STATUS_PENDING,
    PROCUREMENT_STATUS_APPROVED,
    PROCUREMENT_STATUS_ORDERED,
    PROCUREMENT_STATUS_DELIVERED,
    PROCUREMENT_STATUS_COMPLETED,
    PROCUREMENT_STATUS_CANCELLED
)
from backend.app.services.vendor_service import can_vendor_participate


def can_create_procurement_request(vendor_status: str) -> bool:
    """
    Procurement request can be created only for approved vendors.
    """
    return can_vendor_participate(vendor_status)


def approve_procurement_request(current_status: str) -> str:
    """
    Approve procurement request if it is pending.
    """
    if current_status != PROCUREMENT_STATUS_PENDING:
        raise ValueError("Only pending procurement requests can be approved")

    return PROCUREMENT_STATUS_APPROVED


def mark_ordered(current_status: str) -> str:
    """
    Move approved procurement request to ordered stage.
    """
    if current_status != PROCUREMENT_STATUS_APPROVED:
        raise ValueError("Only approved procurement requests can be ordered")

    return PROCUREMENT_STATUS_ORDERED


def mark_delivered(current_status: str) -> str:
    """
    Mark order as delivered after it is ordered.
    """
    if current_status != PROCUREMENT_STATUS_ORDERED:
        raise ValueError("Only ordered purchase orders can be marked delivered")

    return PROCUREMENT_STATUS_DELIVERED


def mark_completed(current_status: str) -> str:
    """
    Mark procurement as completed after delivery.
    """
    if current_status != PROCUREMENT_STATUS_DELIVERED:
        raise ValueError("Only delivered orders can be completed")

    return PROCUREMENT_STATUS_COMPLETED


def cancel_procurement_request(current_status: str) -> str:
    """
    Cancel request unless it is already completed.
    """
    if current_status == PROCUREMENT_STATUS_COMPLETED:
        raise ValueError("Completed procurement cannot be cancelled")

    return PROCUREMENT_STATUS_CANCELLED