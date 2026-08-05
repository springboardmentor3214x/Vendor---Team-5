"""Notification helpers plus deterministic scans for a scheduler/API to call.

Persistence uses ``Notification`` when its model/migration is available. External
email/SMS delivery intentionally remains unconfigured until provider credentials
and transport integration are supplied.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from app.models.certification import Certification
from app.models.contract import Contract
from app.models.invoice import Invoice
from app.models.procurement_request import ProcurementRequest
from app.models.purchase_order import PurchaseOrder
from app.models.user import User
from app.models.vendor import Vendor

try:
    from app.models.notification import Notification  # type: ignore[import-not-found]
except ImportError:  # The migration has not landed on this branch.
    Notification = None


PROCUREMENT_EVENTS = {"submitted", "approval_required", "approved", "rejected", "completed", "high_priority"}
PURCHASE_ORDER_EVENTS = {"created", "delayed", "delivered", "cancelled"}
INVOICE_EVENTS = {"approved", "rejected", "payment_due", "paid"}


def _unavailable(reason: str = "Notification persistence") -> dict[str, str]:
    return {"status": "unavailable", "message": f"{reason} is unavailable until a Swathi H DB/migration change is added."}


def _columns() -> set[str]:
    try:
        return set(Notification.__table__.columns.keys()) if Notification is not None else set()
    except (AttributeError, TypeError):
        return set()


def _rows(db: Any, model: Any) -> list[Any]:
    if db is None:
        return []
    try:
        return list(db.query(model).all() or [])
    except Exception:
        return []


def _first(db: Any, model: Any, entity_id: int) -> Any | None:
    return next((row for row in _rows(db, model) if getattr(row, "id", None) == entity_id), None)


def _value(item: Any, name: str, default: Any = None) -> Any:
    return item.get(name, default) if isinstance(item, dict) else getattr(item, name, default)


def _recipient_id(row: Any, users: list[Any], *, vendor: Any | None = None) -> int | None:
    """Resolve only explicit user links or a verified vendor-email user match."""
    for name in ("responsible_manager_id", "procurement_manager_id", "owner_id", "created_by", "user_id", "contact_user_id", "account_id"):
        value = _value(row, name)
        if isinstance(value, int) and value > 0:
            return value
    for name in ("responsible_manager", "procurement_manager", "owner", "user", "contact_user", "account"):
        value = _value(row, name)
        if isinstance(_value(value, "id"), int) and _value(value, "id") > 0:
            return _value(value, "id")
    candidate = vendor or row
    email = _value(candidate, "email")
    if email:
        matched = next((user for user in users if _value(user, "email") == email), None)
        if matched and isinstance(_value(matched, "id"), int):
            return _value(matched, "id")
    admin = next((user for user in users if _value(user, "role") in {"Administrator", "Admin"}), None)
    return _value(admin, "id") if isinstance(_value(admin, "id"), int) else None


def _vendor_for(db: Any, vendor_id: Any) -> Any | None:
    return next((vendor for vendor in _rows(db, Vendor) if _value(vendor, "id") == vendor_id), None)


def classify_notification_priority(event_type: str, related_module: str | None = None) -> str:
    """Classify known events without relying on an in-app notification table."""
    event = event_type.strip().lower().replace(" ", "_")
    module = (related_module or "").strip().lower()
    if event in {"critical_delivery_delay", "contract_expired", "approval_pending", "approval_required", "high_priority", "delayed"}:
        return "high"
    if event in {"vendor_approved", "invoice_generated", "procurement_assigned", "approved", "payment_due"}:
        return "medium"
    if event in {"profile_updated", "password_changed", "new_message_received", "submitted", "created", "delivered", "paid"}:
        return "low"
    return "high" if module == "compliance" and event in {"expired", "non_compliant"} else "medium"


def create_notification(
    db: Any,
    user_id: int,
    title: str,
    description: str | None = None,
    notification_type: str | None = None,
    related_module: str | None = None,
    related_entity_id: int | None = None,
    priority: str = "medium",
    delivery_method: str = "in_app",
    *,
    message: str | None = None,
) -> Any:
    """Persist a notification only when a compatible Notification model exists."""
    body = description if description is not None else message
    if not isinstance(user_id, int) or user_id <= 0:
        raise ValueError("user_id must be a positive integer.")
    if not title or not title.strip() or not body or not body.strip():
        raise ValueError("title and description are required.")
    if priority not in {"low", "medium", "high"}:
        raise ValueError("priority must be low, medium, or high.")
    if Notification is None or db is None:
        return _unavailable()
    columns = _columns()
    values = {"user_id": user_id, "title": title.strip(), "message": body.strip(), "description": body.strip(),
              "notification_type": notification_type, "related_module": related_module,
              "related_entity_id": related_entity_id, "priority": priority, "delivery_method": delivery_method,
              "is_read": False, "created_at": datetime.utcnow()}
    notification = Notification(**{name: value for name, value in values.items() if name in columns and value is not None})
    try:
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification
    except Exception:
        db.rollback()
        return _unavailable()


def get_user_notifications(db: Any, user_id: int, filters: dict[str, Any] | None = None) -> list[Any]:
    """Read a user's notifications, applying only migrated fields and filters."""
    if Notification is None or db is None:
        return []
    try:
        columns, query = _columns(), db.query(Notification)
        if "user_id" in columns:
            query = query.filter(Notification.user_id == user_id)
        aliases = {"read": "is_read", "module": "related_module", "type": "notification_type"}
        for name, value in (filters or {}).items():
            column = aliases.get(name, name)
            if name == "date_from" and "created_at" in columns and value is not None:
                query = query.filter(Notification.created_at >= value)
            elif name == "date_to" and "created_at" in columns and value is not None:
                query = query.filter(Notification.created_at <= value)
            elif column in columns and value is not None:
                query = query.filter(getattr(Notification, column) == value)
        if "created_at" in columns:
            query = query.order_by(Notification.created_at.desc())
        return list(query.all() or [])
    except Exception:
        return []


def get_unread_notifications(db: Any, user_id: int) -> list[Any]:
    return get_user_notifications(db, user_id, {"is_read": False})


def mark_notification_read(db: Any, notification_id: int, user_id: int) -> Any | None:
    if Notification is None or db is None or "is_read" not in _columns():
        return None
    try:
        query = db.query(Notification).filter(Notification.id == notification_id)
        if "user_id" in _columns():
            query = query.filter(Notification.user_id == user_id)
        notification = query.first()
        if notification is None:
            return None
        notification.is_read = True
        db.commit()
        db.refresh(notification)
        return notification
    except Exception:
        db.rollback()
        return None


def mark_notification_as_read(db: Any, notification_id: int, user_id: int) -> Any | None:
    """Backward-compatible name for earlier service consumers."""
    return mark_notification_read(db, notification_id, user_id)


def mark_all_notifications_read(db: Any, user_id: int) -> int:
    if Notification is None or db is None or "is_read" not in _columns():
        return 0
    notifications = get_user_notifications(db, user_id, {"is_read": False})
    try:
        for notification in notifications:
            notification.is_read = True
        if notifications:
            db.commit()
        return len(notifications)
    except Exception:
        db.rollback()
        return 0


def _event_notification(db: Any, row: Any, user_id: int | None, title: str, description: str, event: str, module: str) -> Any:
    if row is None:
        return _unavailable(f"Requested {module} record")
    if not user_id:
        return _unavailable(f"{module} notification recipient resolution")
    return create_notification(db, user_id, title, description, event, module, getattr(row, "id", None),
                               classify_notification_priority(event, module))


def generate_procurement_alert(db: Any, procurement_request_id: int, event_type: str) -> Any:
    if event_type not in PROCUREMENT_EVENTS:
        raise ValueError("Unsupported procurement event_type.")
    row = _first(db, ProcurementRequest, procurement_request_id)
    title = f"Procurement request {event_type.replace('_', ' ')}"
    return _event_notification(db, row, getattr(row, "requested_by", None) if row else None, title,
                               f"Procurement request {getattr(row, 'request_number', procurement_request_id)} was {event_type.replace('_', ' ')}.",
                               event_type, "procurement")


def generate_purchase_order_notification(db: Any, purchase_order_id: int, event_type: str) -> Any:
    if event_type not in PURCHASE_ORDER_EVENTS:
        raise ValueError("Unsupported purchase order event_type.")
    row = _first(db, PurchaseOrder, purchase_order_id)
    recipient = getattr(row, "created_by", None) or getattr(row, "approved_by", None) if row else None
    return _event_notification(db, row, recipient, f"Purchase order {event_type}",
                               f"Purchase order {getattr(row, 'po_number', purchase_order_id)} was {event_type}.", event_type, "purchase_order")


def generate_vendor_approval_notification(db: Any, vendor_id: int, approved: bool = True, reason: str | None = None) -> Any:
    vendor = _vendor_for(db, vendor_id)
    if vendor is None:
        return _unavailable("Requested vendor record")
    recipient = _recipient_id(vendor, _rows(db, User))
    if recipient is None:
        return _unavailable("Vendor approval notification recipient resolution")
    outcome = "approved" if approved else "rejected"
    detail = reason or f"Vendor registration was {outcome}."
    return create_notification(db, recipient, f"Vendor registration {outcome}", detail,
                               "vendor_approval", "vendor", vendor_id,
                               classify_notification_priority("approved" if approved else "rejected", "vendor"))


def _expiry_result(rows: list[Any], days_before: int | None, entity_name: str, date_name: str) -> dict[str, Any]:
    windows = {90, 30, 7, 1} if days_before is None else {days_before}
    today = date.today()
    matches = [row for row in rows if (expiry := getattr(row, date_name, None)) and
               (expiry.date() if isinstance(expiry, datetime) else expiry) >= today and
               ((expiry.date() if isinstance(expiry, datetime) else expiry) - today).days in windows]
    return {"generated_count": 0, "generated": [], "matched_entity_ids": [getattr(row, "id", None) for row in matches],
            "status": "unavailable" if matches else "ready",
            "message": f"{entity_name} expiry recipients and notification persistence require Swathi H DB/migration support." if matches else None}


def generate_contract_expiry_notifications(db: Any, days_before: int | None = None) -> dict[str, Any]:
    rows, users = _rows(db, Contract), _rows(db, User)
    result = _expiry_result(rows, days_before, "Contract", "end_date")
    generated = []
    for contract in (row for row in rows if getattr(row, "id", None) in result["matched_entity_ids"]):
        recipient = _recipient_id(contract, users, vendor=_vendor_for(db, _value(contract, "vendor_id")))
        if recipient is not None:
            generated.append(create_contract_expiry_notification(db, recipient, _value(contract, "id"),
                                                                  (_value(contract, "end_date").date() if isinstance(_value(contract, "end_date"), datetime) else _value(contract, "end_date") - date.today()).days))
    result["generated"] = generated
    result["generated_count"] = len(generated)
    if result["matched_entity_ids"] and not generated:
        result.update(_unavailable("Contract expiry notification recipient resolution"))
    return result


def generate_compliance_expiry_notifications(db: Any, days_before: int | None = None) -> dict[str, Any]:
    rows, users = _rows(db, Certification), _rows(db, User)
    result = _expiry_result(rows, days_before, "Certification", "expiry_date")
    generated = []
    for certification in (row for row in rows if getattr(row, "id", None) in result["matched_entity_ids"]):
        recipient = _recipient_id(certification, users, vendor=_vendor_for(db, _value(certification, "vendor_id")))
        if recipient is not None:
            generated.append(create_compliance_notification(db, recipient, _value(certification, "vendor_id"),
                                                            f"Certification expires in {(_value(certification, 'expiry_date').date() if isinstance(_value(certification, 'expiry_date'), datetime) else _value(certification, 'expiry_date') - date.today()).days} days."))
    result["generated"] = generated
    result["generated_count"] = len(generated)
    if result["matched_entity_ids"] and not generated:
        result.update(_unavailable("Compliance expiry notification recipient resolution"))
    return result


def create_contract_expiry_notification(db: Any, user_id: int, contract_id: int, days_until_expiry: int) -> Any:
    """Backward-compatible single-recipient contract reminder helper."""
    return create_notification(db, user_id, "Contract expiry reminder",
                               f"Contract {contract_id} expires in {days_until_expiry} days.",
                               "contract_expiry", "contract", contract_id,
                               classify_notification_priority("contract_expired", "contract"))


def create_compliance_notification(db: Any, user_id: int, vendor_id: int, message: str) -> Any:
    """Backward-compatible compliance notification helper."""
    return create_notification(db, user_id, "Compliance update", message, "compliance", "compliance", vendor_id,
                               classify_notification_priority("non_compliant", "compliance"))


def generate_invoice_notification(db: Any, invoice_id: int, event_type: str) -> Any:
    if event_type not in INVOICE_EVENTS:
        raise ValueError("Unsupported invoice event_type.")
    invoice = _first(db, Invoice, invoice_id)
    order = _first(db, PurchaseOrder, getattr(invoice, "purchase_order_id", None)) if invoice else None
    recipient = getattr(order, "created_by", None) or getattr(order, "approved_by", None) if order else None
    return _event_notification(db, invoice, recipient, f"Invoice {event_type.replace('_', ' ')}",
                               f"Invoice {getattr(invoice, 'invoice_number', invoice_id)} was {event_type.replace('_', ' ')}.", event_type, "invoice")


def build_email_notification_payload(notification: Any, recipient: Any) -> dict[str, Any]:
    email = _value(recipient, "email") if not isinstance(recipient, str) else recipient
    if not email:
        return _unavailable("Email recipient")
    return {"status": "not_configured", "channel": "email", "to": email, "subject": _value(notification, "title"),
            "body": _value(notification, "description", _value(notification, "message")), "notification_id": _value(notification, "id")}


def build_sms_notification_payload(notification: Any, recipient: Any) -> dict[str, Any]:
    phone = _value(recipient, "mobile_number", _value(recipient, "phone_number")) if not isinstance(recipient, str) else recipient
    if not phone:
        return _unavailable("SMS recipient")
    return {"status": "not_configured", "channel": "sms", "to": phone,
            "body": f"{_value(notification, 'title')}: {_value(notification, 'description', _value(notification, 'message'))}",
            "notification_id": _value(notification, "id")}


def send_email_notification(*args: Any, **kwargs: Any) -> dict[str, str]:
    """Provider integration requires SMTP configuration and credentials."""
    del args, kwargs
    return {"status": "not_configured", "channel": "email", "message": "SMTP provider delivery is not configured."}


def send_sms_notification(*args: Any, **kwargs: Any) -> dict[str, str]:
    """Provider integration requires SMS credentials and a configured transport."""
    del args, kwargs
    return {"status": "not_configured", "channel": "sms", "message": "SMS provider delivery is not configured."}


def scan_contract_expiry_notifications(db: Any, days_before: int | None = None) -> dict[str, Any]:
    """Deterministic contract-expiry scan; scheduler registration is intentionally external."""
    return generate_contract_expiry_notifications(db, days_before)


def scan_compliance_expiry_notifications(db: Any, days_before: int | None = None) -> dict[str, Any]:
    """Deterministic certification-expiry scan; scheduler registration is intentionally external."""
    return generate_compliance_expiry_notifications(db, days_before)


def scan_delayed_purchase_order_notifications(db: Any) -> dict[str, Any]:
    """Find overdue PO/delivery rows and generate only safely-addressed notifications."""
    today, generated, matched = date.today(), [], []
    for order in _rows(db, PurchaseOrder):
        expected = _value(order, "expected_delivery_date") or _value(order, "delivery_date")
        expected_day = expected.date() if isinstance(expected, datetime) else expected
        status = (_value(order, "po_status") or _value(order, "status") or "").lower()
        if not expected_day or expected_day >= today or status in {"delivered", "completed", "cancelled"}:
            continue
        matched.append(_value(order, "id"))
        recipient = _recipient_id(order, _rows(db, User), vendor=_vendor_for(db, _value(order, "vendor_id")))
        if recipient is None:
            continue
        generated.append(create_notification(db, recipient, "Purchase order delivery delayed",
                                             f"Purchase order {_value(order, 'po_number', _value(order, 'id'))} is overdue.",
                                             "delivery_delay", "procurement", _value(order, "id"), "high"))
    return {"status": "ready" if not matched or generated else "unavailable", "matched_entity_ids": matched,
            "generated": generated, "generated_count": len(generated),
            "message": None if not matched or generated else "Delayed purchase-order recipient resolution is unavailable."}


def scan_for_pending_notifications(db: Any) -> dict[str, Any]:
    """Compatibility aggregate for scheduler/API layers; does not create scheduler infrastructure."""
    return {"contract_expiry": scan_contract_expiry_notifications(db),
            "delivery_delay": scan_delayed_purchase_order_notifications(db),
            "compliance_expiry": scan_compliance_expiry_notifications(db)}


def get_notification_summary(db: Any, user_id: int) -> dict[str, Any]:
    notifications = get_user_notifications(db, user_id)
    return {"total_notifications": len(notifications), "unread_count": len(get_unread_notifications(db, user_id)),
            "high_priority_count": sum(_value(row, "priority") == "high" for row in notifications),
            "recent_notifications": notifications[:5]}
