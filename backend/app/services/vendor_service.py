from backend.app.utils.constants import (
    VENDOR_STATUS_PENDING,
    VENDOR_STATUS_APPROVED,
    VENDOR_STATUS_REJECTED,
    VENDOR_CATEGORIES
)


def validate_vendor_category(category: str) -> bool:
    """
    Check whether vendor category is valid.
    """
    return category in VENDOR_CATEGORIES


def can_vendor_participate(status: str) -> bool:
    """
    Only approved vendors are eligible for procurement.
    """
    return status == VENDOR_STATUS_APPROVED


def approve_vendor(current_status: str) -> str:
    """
    Approve vendor if current status is pending.
    """
    if current_status != VENDOR_STATUS_PENDING:
        raise ValueError("Only pending vendors can be approved")

    return VENDOR_STATUS_APPROVED


def reject_vendor(current_status: str) -> str:
    """
    Reject vendor if current status is pending.
    """
    if current_status != VENDOR_STATUS_PENDING:
        raise ValueError("Only pending vendors can be rejected")

    return VENDOR_STATUS_REJECTED


def get_vendor_status_message(status: str) -> str:
    """
    Return readable message for vendor status.
    """
    if status == VENDOR_STATUS_PENDING:
        return "Vendor registration is pending approval"
    if status == VENDOR_STATUS_APPROVED:
        return "Vendor is approved and eligible for procurement"
    if status == VENDOR_STATUS_REJECTED:
        return "Vendor registration has been rejected"

    return "Invalid vendor status"