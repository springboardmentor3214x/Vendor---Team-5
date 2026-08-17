from app.utils.constants import (
    PROCUREMENT_REQUEST_STATUS_PENDING,
    PROCUREMENT_REQUEST_STATUS_DRAFT,
    PROCUREMENT_REQUEST_STATUS_APPROVED,
    PROCUREMENT_REQUEST_STATUS_REJECTED,
    PROCUREMENT_REQUEST_STATUS_CANCELLED,
    PROCUREMENT_REQUEST_STATUS_SENT_BACK,
    ROLE_ADMIN,
    ROLE_PROCUREMENT_MANAGER
)


def submit_procurement_request(current_status: str) -> str:
    """Submit a draft request for review without allowing terminal states to reopen."""
    if current_status != PROCUREMENT_REQUEST_STATUS_DRAFT:
        raise ValueError("Only draft procurement requests can be submitted")
    return PROCUREMENT_REQUEST_STATUS_PENDING


def validate_procurement_request_for_submission(request: object) -> None:
    """Validate fields the current request model requires before a draft is submitted."""
    required = ("title", "department", "item_description", "product_name", "product_category",
                "estimated_budget", "required_delivery_date", "business_justification")
    missing = [field for field in required if getattr(request, field, None) in (None, "")]
    if missing:
        raise ValueError("Missing required procurement request fields: " + ", ".join(missing))
    quantity = getattr(request, "quantity", 1)
    budget = getattr(request, "estimated_budget", 0)
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
        raise ValueError("Procurement request quantity must be greater than zero")
    if isinstance(budget, bool) or not isinstance(budget, (int, float)) or budget < 0:
        raise ValueError("Procurement request estimated budget cannot be negative")


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
