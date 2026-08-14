"""Issue/complaint business rules and performance-history shaping."""

from datetime import datetime
from typing import Any

from app.models.vendor_issue import VendorIssue

OPEN_STATUSES = frozenset({"Open", "In Progress", "Escalated"})
CLOSED_STATUSES = frozenset({"Resolved", "Closed"})


def create_vendor_issue(db: Any, **values: Any) -> VendorIssue:
    """Persist an issue, rejecting resolved records without a resolution note."""
    _validate_issue_values(values)
    issue = VendorIssue(**values)
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue


def get_vendor_issue(db: Any, issue_id: int) -> VendorIssue | None:
    return db.query(VendorIssue).filter(VendorIssue.id == issue_id).first()


def list_vendor_issues(db: Any, vendor_id: int, *, include_closed: bool = True) -> list[VendorIssue]:
    issues = db.query(VendorIssue).filter(VendorIssue.vendor_id == vendor_id).all()
    return issues if include_closed else [issue for issue in issues if issue.status in OPEN_STATUSES]


def update_vendor_issue(db: Any, issue_id: int, *, updated_by: int | None = None, **changes: Any) -> VendorIssue | None:
    issue = get_vendor_issue(db, issue_id)
    if issue is None:
        return None
    _validate_issue_values(changes, existing=issue)
    for field, value in changes.items():
        if value is not None and hasattr(issue, field):
            setattr(issue, field, value)
    if issue.status in CLOSED_STATUSES and issue.resolved_date is None:
        issue.resolved_date = datetime.utcnow()
        issue.resolved_by = updated_by
    elif issue.status in OPEN_STATUSES:
        issue.resolved_date = None
        issue.resolved_by = None
    db.commit()
    db.refresh(issue)
    return issue


def resolve_vendor_issue(db: Any, issue_id: int, *, resolution_notes: str, resolved_by: int) -> VendorIssue | None:
    if not resolution_notes or not resolution_notes.strip():
        raise ValueError("Resolution notes are required when resolving an issue")
    return update_vendor_issue(db, issue_id, updated_by=resolved_by, status="Resolved", resolution_notes=resolution_notes)


def vendor_issue_performance_history(db: Any, vendor_id: int) -> list[dict[str, Any]]:
    """Return audit-safe issue history for composition into performance history."""
    return [
        {
            "issue_id": issue.id,
            "purchase_order_id": issue.purchase_order_id,
            "category": issue.issue_category,
            "severity": issue.severity,
            "status": issue.status,
            "reported_date": issue.reported_date,
            "resolved_date": issue.resolved_date,
            "resolution_notes": issue.resolution_notes,
        }
        for issue in list_vendor_issues(db, vendor_id)
    ]


def _validate_issue_values(values: dict[str, Any], existing: VendorIssue | None = None) -> None:
    status = values.get("status", getattr(existing, "status", "Open"))
    if status not in OPEN_STATUSES | CLOSED_STATUSES:
        raise ValueError("Unsupported issue status")
    notes = values.get("resolution_notes", getattr(existing, "resolution_notes", None))
    if status in CLOSED_STATUSES and not notes:
        raise ValueError("Resolution notes are required when closing an issue")
