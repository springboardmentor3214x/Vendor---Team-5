from datetime import date, timedelta

import pytest

from app.services.contract_compliance_service import (
    calculate_certification_dashboard_summary, calculate_compliance_percentage,
    calculate_contract_dashboard_summary, calculate_contract_duration_days,
    calculate_days_until_expiry, can_user_manage_contract, can_user_view_contract,
    determine_contract_status, filter_contracts_by_status,
    generate_certification_expiry_notification, generate_contract_expiry_notification,
    get_contract_renewal_reminder_level, is_certification_expired,
    is_certification_expiring_soon, is_contract_expiring_soon, sort_contracts_by_expiry,
    validate_contract_dates, validate_contract_value, validate_required_contract_fields,
    validate_vendor_document_type, verify_compliance_status,
)


TODAY = date(2026, 7, 27)


def make_contract(**overrides):
    contract = {
        "contract_number": "CON-001", "contract_title": "Steel Supply", "vendor_id": 1,
        "contract_type": "Supply", "procurement_category": "Raw Materials",
        "start_date": date(2026, 1, 1), "end_date": date(2026, 12, 31),
        "contract_value": 100000.0, "payment_terms": "Net 30",
        "responsible_manager": "Sonali", "vendor_name": "ABC Steel", "renewal_status": "Pending",
    }
    contract.update(overrides)
    return contract


def test_valid_and_invalid_contract_dates():
    assert validate_contract_dates(date(2026, 1, 1), date(2026, 1, 2)) is True
    with pytest.raises(ValueError):
        validate_contract_dates(date(2026, 1, 2), date(2026, 1, 2))


def test_contract_duration_and_days_until_expiry():
    assert calculate_contract_duration_days(date(2026, 1, 1), date(2026, 2, 1)) == 31
    assert calculate_days_until_expiry(date(2026, 8, 6), TODAY) == 10


@pytest.mark.parametrize(("start", "end", "expected"), [
    (date(2026, 8, 1), date(2026, 12, 1), "Draft"),
    (date(2026, 1, 1), date(2026, 12, 1), "Active"),
    (date(2026, 1, 1), date(2026, 7, 1), "Expired"),
])
def test_contract_statuses(start, end, expected):
    assert determine_contract_status(start, end, TODAY) == expected


def test_contract_expiring_soon_and_expired_false():
    assert is_contract_expiring_soon(date(2026, 8, 26), TODAY) is True
    assert is_contract_expiring_soon(date(2026, 7, 26), TODAY) is False


@pytest.mark.parametrize(("days", "expected"), [
    (90, "90 Days Before Expiry"), (30, "30 Days Before Expiry"),
    (7, "7 Days Before Expiry"), (0, "On Expiry Date"),
])
def test_contract_renewal_reminder_levels(days, expected):
    assert get_contract_renewal_reminder_level(TODAY + timedelta(days=days), TODAY) == expected


def test_contract_expiry_notifications():
    contract = make_contract(end_date=TODAY.fromordinal(TODAY.toordinal() + 30))
    notification = generate_contract_expiry_notification(contract, TODAY)
    assert notification["remaining_days"] == 30
    assert notification["contract_number"] == "CON-001"
    assert generate_contract_expiry_notification(make_contract(end_date=date(2026, 9, 1)), TODAY) is None


def test_contract_value_and_required_fields_validation():
    assert validate_contract_value(1) is True
    assert validate_required_contract_fields(make_contract()) is True
    with pytest.raises(ValueError):
        validate_contract_value(0)
    with pytest.raises(ValueError):
        validate_required_contract_fields(make_contract(contract_title=""))


@pytest.mark.parametrize(("requirements", "expected"), [
    ([{"status": "Compliant"}], "Compliant"),
    ([], "Pending Verification"),
    ([{"status": "Non-Compliant"}], "Non-Compliant"),
    ([{"status": "Expired"}], "Expired"),
])
def test_compliance_statuses(requirements, expected):
    assert verify_compliance_status(requirements) == expected


def test_compliance_percentage_and_empty_list():
    assert calculate_compliance_percentage([{"status": "Compliant"}, {"status": "Pending Verification"}]) == 50
    assert calculate_compliance_percentage([]) == 0


def test_certification_expiry_and_notification():
    certification = {
        "certification_name": "ISO 9001", "certificate_number": "ISO-123",
        "vendor_name": "ABC Steel", "expiry_date": date(2026, 8, 6),
    }
    assert is_certification_expired(date(2026, 7, 26), TODAY) is True
    assert is_certification_expiring_soon(certification["expiry_date"], TODAY) is True
    assert generate_certification_expiry_notification(certification, TODAY)["remaining_days"] == 10


def test_document_type_and_contract_permissions():
    with pytest.raises(ValueError):
        validate_vendor_document_type("Invalid")
    assert can_user_manage_contract("Administrator") is True
    assert can_user_manage_contract("Procurement Manager") is True
    assert can_user_manage_contract("Vendor") is False
    for role in ("Administrator", "Procurement Manager", "Vendor", "Finance Officer", "Auditor"):
        assert can_user_view_contract(role) is True


def test_contract_and_certification_dashboard_summaries():
    contracts = [
        make_contract(end_date=date(2026, 8, 1)),
        make_contract(contract_number="CON-002", end_date=date(2026, 7, 1)),
        make_contract(contract_number="CON-003", start_date=date(2026, 8, 1), end_date=date(2026, 12, 1)),
    ]
    assert calculate_contract_dashboard_summary(contracts, TODAY) == {
        "total_contracts": 3, "active_contracts": 1, "expiring_contracts": 1, "expired_contracts": 1,
    }
    certifications = [{"expiry_date": date(2026, 7, 1)}, {"expiry_date": date(2026, 8, 1)}]
    assert calculate_certification_dashboard_summary(certifications, TODAY) == {
        "total_certifications": 2, "expired_certifications": 1, "expiring_certifications": 1,
    }


def test_filter_sort_and_empty_list_handling():
    contracts = [
        make_contract(contract_number="CON-1", end_date=date(2026, 9, 1)),
        make_contract(contract_number="CON-2", end_date=date(2026, 7, 1)),
    ]
    assert [item["contract_number"] for item in filter_contracts_by_status(contracts, "Expired", TODAY)] == ["CON-2"]
    assert [item["contract_number"] for item in sort_contracts_by_expiry(contracts)] == ["CON-2", "CON-1"]
    assert calculate_contract_dashboard_summary([], TODAY)["total_contracts"] == 0
    assert calculate_certification_dashboard_summary([], TODAY)["total_certifications"] == 0
