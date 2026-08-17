from app.utils.constants import (
    VENDOR_STATUS_PENDING,
    VENDOR_STATUS_APPROVED,
    VENDOR_STATUS_REJECTED,
    VENDOR_STATUS_ACTIVE,
    VENDOR_CATEGORIES,
    ALLOWED_DOCUMENT_EXTENSIONS,
    MAX_DOCUMENT_SIZE_MB
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

def can_vendor_be_assigned_to_procurement(
    approval_status: str,
    vendor_status: str
) -> bool:
    """
    Vendor can be assigned to procurement only if approval status is approved
    and vendor status is active.
    """
    return (
        approval_status == VENDOR_STATUS_APPROVED
        and vendor_status == VENDOR_STATUS_ACTIVE
    )


def validate_vendor_document(file_name: str, file_size_mb: float) -> bool:
    """
    Validate vendor document extension and size.
    Allowed formats: PDF, JPG, JPEG, PNG.
    Maximum size: 5 MB.
    """
    file_name = file_name.lower()

    is_valid_extension = any(
        file_name.endswith(extension)
        for extension in ALLOWED_DOCUMENT_EXTENSIONS
    )

    return is_valid_extension and file_size_mb <= MAX_DOCUMENT_SIZE_MB


def validate_unique_vendor_fields(
    email_exists: bool,
    gst_exists: bool,
    pan_exists: bool,
    registration_number_exists: bool
) -> bool:
    """
    Return True only if email, GST, PAN, and registration number are unique.
    Actual database duplicate check will be done in API/repository layer.
    """
    return not any([
        email_exists,
        gst_exists,
        pan_exists,
        registration_number_exists
    ])