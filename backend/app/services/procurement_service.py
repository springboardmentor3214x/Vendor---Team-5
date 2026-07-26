from app.utils.constants import (
    PROCUREMENT_REQUEST_STATUS_PENDING,
    PROCUREMENT_REQUEST_STATUS_APPROVED,
    PROCUREMENT_REQUEST_STATUS_REJECTED,
    PROCUREMENT_REQUEST_STATUS_CANCELLED,
    PROCUREMENT_REQUEST_STATUS_SENT_BACK,
    ROLE_ADMIN,
    ROLE_PROCUREMENT_MANAGER
)


def approve_procurement_request(current_status: str) -> str:
    """
    Approve procurement request if it is pending.
    """
    if current_status != PROCUREMENT_REQUEST_STATUS_PENDING:
        raise ValueError("Only pending procurement requests can be approved")

    return PROCUREMENT_REQUEST_STATUS_APPROVED


def reject_procurement_request(current_status: str) -> str:
    """
    Reject a procurement request if it is pending.
    """
    if current_status != PROCUREMENT_REQUEST_STATUS_PENDING:
        raise ValueError("Only pending procurement requests can be rejected")

    return PROCUREMENT_REQUEST_STATUS_REJECTED


def cancel_procurement_request(current_status: str) -> str:
    """
    Cancel a pending or approved procurement request.
    """
    if current_status not in [
        PROCUREMENT_REQUEST_STATUS_PENDING,
        PROCUREMENT_REQUEST_STATUS_APPROVED
    ]:
        raise ValueError("Only pending or approved procurement requests can be cancelled")

    return PROCUREMENT_REQUEST_STATUS_CANCELLED


def can_send_back_procurement_request(current_status: str) -> bool:
    """Return whether a pending or approved request can be sent back for changes."""
    return current_status in {
        PROCUREMENT_REQUEST_STATUS_PENDING,
        PROCUREMENT_REQUEST_STATUS_APPROVED,
    }


def can_edit_sent_back_request(current_status: str) -> bool:
    """Return whether a sent-back request is editable."""
    return current_status == PROCUREMENT_REQUEST_STATUS_SENT_BACK


def resubmit_procurement_request(current_status: str) -> str:
    """Return a sent-back procurement request to pending review."""
    if not can_edit_sent_back_request(current_status):
        raise ValueError("Only sent-back procurement requests can be resubmitted")
    return PROCUREMENT_REQUEST_STATUS_PENDING

def generate_procurement_request_number(sequence_number: int) -> str:
    """
    Generate procurement request number automatically.
    Example: PR-2026-0001
    """
    _validate_sequence_number(sequence_number)
    return f"PR-2026-{sequence_number:04d}"


def can_assign_vendor_to_request(request_status: str) -> bool:
    """
    Vendor can be assigned only after procurement request is approved.
    """
    return request_status == PROCUREMENT_REQUEST_STATUS_APPROVED


def can_user_manage_procurement_request(user_role: str) -> bool:
    """
    Only Admin and Procurement Manager can update procurement status.
    """
    return user_role in [ROLE_ADMIN, ROLE_PROCUREMENT_MANAGER]


def _validate_sequence_number(sequence_number: int) -> None:
    if isinstance(sequence_number, bool) or not isinstance(sequence_number, int):
        raise ValueError("Sequence number must be a positive integer")
    if sequence_number <= 0:
        raise ValueError("Sequence number must be a positive integer")
