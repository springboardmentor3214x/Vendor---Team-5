from datetime import date


CONTRACT_STATUS_DRAFT = "Draft"
CONTRACT_STATUS_ACTIVE = "Active"
CONTRACT_STATUS_EXPIRED = "Expired"
CONTRACT_STATUS_RENEWED = "Renewed"
CONTRACT_STATUS_TERMINATED = "Terminated"

COMPLIANCE_COMPLIANT = "Compliant"
COMPLIANCE_PENDING = "Pending Verification"
COMPLIANCE_NON_COMPLIANT = "Non-Compliant"
COMPLIANCE_EXPIRED = "Expired"

RENEWAL_REMINDER_90 = 90
RENEWAL_REMINDER_30 = 30
RENEWAL_REMINDER_7 = 7
RENEWAL_REMINDER_0 = 0

ALLOWED_DOCUMENT_TYPES = {
    "GST Certificate", "PAN Card", "Company Registration Certificate", "Business License",
    "Bank Details", "Insurance Documents", "Product Catalog", "NDA Documents",
    "Service Agreements", "Quality Certificates",
}

CONTRACT_MANAGER_ROLES = {"Administrator", "Procurement Manager"}
CONTRACT_VIEWER_ROLES = CONTRACT_MANAGER_ROLES | {"Vendor", "Finance Officer", "Auditor"}


def _validate_date(value: date, field_name: str = "date") -> None:
    if not isinstance(value, date):
        raise ValueError(f"{field_name} must be a date object.")


def _get_current_date(current_date: date | None) -> date:
    if current_date is None:
        return date.today()
    _validate_date(current_date, "current_date")
    return current_date


def validate_contract_dates(start_date: date, end_date: date) -> bool:
    """Validate that a contract has a positive date range."""
    _validate_date(start_date, "start_date")
    _validate_date(end_date, "end_date")
    if end_date <= start_date:
        raise ValueError("end_date must be after start_date.")
    return True


def calculate_contract_duration_days(start_date: date, end_date: date) -> int:
    """Return the number of days in a valid contract period."""
    validate_contract_dates(start_date, end_date)
    return (end_date - start_date).days


def calculate_days_until_expiry(end_date: date, current_date: date | None = None) -> int:
    """Return remaining days, including a negative value for expired contracts."""
    _validate_date(end_date, "end_date")
    return (end_date - _get_current_date(current_date)).days


def determine_contract_status(
    start_date: date, end_date: date, current_date: date | None = None
) -> str:
    """Compute the contract's current lifecycle status from its dates."""
    validate_contract_dates(start_date, end_date)
    today = _get_current_date(current_date)
    if today < start_date:
        return CONTRACT_STATUS_DRAFT
    if today <= end_date:
        return CONTRACT_STATUS_ACTIVE
    return CONTRACT_STATUS_EXPIRED


def is_contract_expiring_soon(
    end_date: date, current_date: date | None = None, reminder_days: int = 30
) -> bool:
    """Return whether a non-expired contract expires within the reminder window."""
    if reminder_days < 0:
        raise ValueError("reminder_days must not be negative.")
    days_remaining = calculate_days_until_expiry(end_date, current_date)
    return 0 <= days_remaining <= reminder_days


def get_contract_renewal_reminder_level(
    end_date: date, current_date: date | None = None
) -> str | None:
    """Return an exact configured renewal reminder level, if one applies."""
    days_remaining = calculate_days_until_expiry(end_date, current_date)
    reminder_messages = {
        RENEWAL_REMINDER_90: "90 Days Before Expiry",
        RENEWAL_REMINDER_30: "30 Days Before Expiry",
        RENEWAL_REMINDER_7: "7 Days Before Expiry",
        RENEWAL_REMINDER_0: "On Expiry Date",
    }
    return reminder_messages.get(days_remaining)


def generate_contract_expiry_notification(
    contract: dict, current_date: date | None = None
) -> dict | None:
    """Build a renewal notification only at an exact reminder interval."""
    end_date = contract["end_date"]
    reminder_level = get_contract_renewal_reminder_level(end_date, current_date)
    if reminder_level is None:
        return None
    remaining_days = calculate_days_until_expiry(end_date, current_date)
    return {
        "contract_number": contract["contract_number"],
        "vendor_name": contract["vendor_name"],
        "expiry_date": end_date,
        "remaining_days": remaining_days,
        "renewal_status": contract["renewal_status"],
        "message": f"Contract {contract['contract_number']} for {contract['vendor_name']} expires: {reminder_level}.",
    }


def validate_contract_value(contract_value: float) -> bool:
    """Ensure a contract has a positive value."""
    if contract_value <= 0:
        raise ValueError("contract_value must be greater than 0.")
    return True


def validate_required_contract_fields(contract_data: dict) -> bool:
    """Validate required contract repository fields and core values."""
    required_fields = (
        "contract_number", "contract_title", "vendor_id", "contract_type",
        "procurement_category", "start_date", "end_date", "contract_value",
        "payment_terms", "responsible_manager",
    )
    for field in required_fields:
        value = contract_data.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValueError(f"{field} is required.")
    validate_contract_dates(contract_data["start_date"], contract_data["end_date"])
    validate_contract_value(contract_data["contract_value"])
    return True


def verify_compliance_status(requirements: list[dict]) -> str:
    """Determine the aggregate compliance status, prioritizing the most severe state."""
    if not requirements:
        return COMPLIANCE_PENDING
    statuses = {requirement.get("status") for requirement in requirements}
    if COMPLIANCE_EXPIRED in statuses:
        return COMPLIANCE_EXPIRED
    if COMPLIANCE_NON_COMPLIANT in statuses:
        return COMPLIANCE_NON_COMPLIANT
    if COMPLIANCE_PENDING in statuses:
        return COMPLIANCE_PENDING
    return COMPLIANCE_COMPLIANT


def calculate_compliance_percentage(requirements: list[dict]) -> float:
    """Return the percentage of requirements explicitly marked compliant."""
    if not requirements:
        return 0
    compliant_count = sum(
        requirement.get("status") == COMPLIANCE_COMPLIANT for requirement in requirements
    )
    return round(compliant_count / len(requirements) * 100, 2)


def is_certification_expired(expiry_date: date, current_date: date | None = None) -> bool:
    """Return whether a certification's expiry date has passed."""
    return calculate_days_until_expiry(expiry_date, current_date) < 0


def is_certification_expiring_soon(
    expiry_date: date, current_date: date | None = None, reminder_days: int = 30
) -> bool:
    """Return whether a non-expired certification expires within the reminder window."""
    return is_contract_expiring_soon(expiry_date, current_date, reminder_days)


def generate_certification_expiry_notification(
    certification: dict, current_date: date | None = None
) -> dict | None:
    """Build a notification for an active certification expiring within 30 days."""
    expiry_date = certification["expiry_date"]
    if not is_certification_expiring_soon(expiry_date, current_date):
        return None
    remaining_days = calculate_days_until_expiry(expiry_date, current_date)
    return {
        "certification_name": certification["certification_name"],
        "certificate_number": certification["certificate_number"],
        "vendor_name": certification["vendor_name"],
        "expiry_date": expiry_date,
        "remaining_days": remaining_days,
        "message": f"Certification {certification['certification_name']} expires in {remaining_days} days.",
    }


def validate_vendor_document_type(document_type: str) -> bool:
    """Validate a vendor document type supported by the repository."""
    if document_type not in ALLOWED_DOCUMENT_TYPES:
        raise ValueError("Invalid vendor document type.")
    return True


def can_user_manage_contract(role: str) -> bool:
    """Return whether a role may manage contracts."""
    return role in CONTRACT_MANAGER_ROLES


def can_user_view_contract(role: str) -> bool:
    """Return whether a role may view contracts."""
    return role in CONTRACT_VIEWER_ROLES


def calculate_contract_dashboard_summary(
    contracts: list[dict], current_date: date | None = None
) -> dict:
    """Calculate dashboard contract counts without mutating contract records."""
    today = _get_current_date(current_date)
    active_contracts = 0
    expiring_contracts = 0
    expired_contracts = 0
    for contract in contracts:
        status = determine_contract_status(contract["start_date"], contract["end_date"], today)
        if status == CONTRACT_STATUS_ACTIVE:
            active_contracts += 1
            if is_contract_expiring_soon(contract["end_date"], today):
                expiring_contracts += 1
        elif status == CONTRACT_STATUS_EXPIRED:
            expired_contracts += 1
    return {
        "total_contracts": len(contracts),
        "active_contracts": active_contracts,
        "expiring_contracts": expiring_contracts,
        "expired_contracts": expired_contracts,
    }


def calculate_certification_dashboard_summary(
    certifications: list[dict], current_date: date | None = None
) -> dict:
    """Calculate dashboard certification expiry counts."""
    today = _get_current_date(current_date)
    expired = sum(is_certification_expired(item["expiry_date"], today) for item in certifications)
    expiring = sum(is_certification_expiring_soon(item["expiry_date"], today) for item in certifications)
    return {
        "total_certifications": len(certifications),
        "expired_certifications": expired,
        "expiring_certifications": expiring,
    }


def filter_contracts_by_status(
    contracts: list[dict], status: str, current_date: date | None = None
) -> list[dict]:
    """Return contracts whose computed status matches the requested status."""
    today = _get_current_date(current_date)
    return [
        contract for contract in contracts
        if determine_contract_status(contract["start_date"], contract["end_date"], today) == status
    ]


def sort_contracts_by_expiry(contracts: list[dict]) -> list[dict]:
    """Return contracts ordered by nearest expiry without modifying the input list."""
    return sorted(contracts, key=lambda contract: contract["end_date"])
