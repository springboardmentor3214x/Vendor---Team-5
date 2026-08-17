"""Module 9 Notification Service handling in-app, email, SMS alerts, priority management, and automated background triggers."""

from __future__ import annotations

from datetime import datetime, date, timedelta
from email.message import EmailMessage
import os
import smtplib
from typing import Any, List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from types import SimpleNamespace
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import base64

from app.models.notification import Notification
from app.models.contract import Contract
from app.models.purchase_order import PurchaseOrder
from app.models.certification import Certification
from app.models.compliance import ComplianceRecord
from app.models.user import User
from app.models.vendor import Vendor


def _column_names() -> set[str]:
    try:
        return set(Notification.__table__.columns.keys()) if Notification is not None else set()
    except (AttributeError, TypeError):
        return set()


def _legacy_notification_rows(
    db: Session, user_id: int, module: Optional[str], priority: Optional[str], is_read: Optional[bool]
) -> List[Any]:
    """Read legacy notification rows without selecting columns not yet migrated."""
    available = {column["name"] for column in inspect(db.bind).get_columns("notifications")}
    selected = [getattr(Notification, name) for name in _column_names() if name in available]
    if not selected:
        return []
    query = db.query(*selected).filter(Notification.user_id == user_id)
    if module and "related_module" in available:
        query = query.filter(Notification.related_module.ilike(f"%{module}%"))
    if priority and "priority" in available:
        query = query.filter(Notification.priority == priority.upper())
    if is_read is not None and "is_read" in available:
        query = query.filter(Notification.is_read == is_read)
    if "created_at" in available:
        query = query.order_by(Notification.created_at.desc())
    defaults = {"vendor_id": None, "contract_id": None, "purchase_order_id": None,
                "procurement_request_id": None, "notification_type": "INFO", "related_module": None,
                "related_record_id": None, "priority": "MEDIUM", "delivery_method": "IN_APP",
                "is_read": False, "read_at": None, "link": None, "created_at": None}
    return [SimpleNamespace(**{**defaults, **dict(row._mapping)}) for row in query.all()]


def get_user_notifications(
    db: Session,
    user_id: int,
    module: Optional[str] = None,
    priority: Optional[str] = None,
    is_read: Optional[bool] = None,
    filters: Optional[Dict[str, Any]] = None,
) -> List[Notification]:
    """Retrieve notifications owned by user_id with optional filters."""
    if db is None or Notification is None:
        return []
    if isinstance(module, dict):  # Legacy Module 7/10 positional filters argument.
        filters, module = module, None
    query = db.query(Notification)
    if hasattr(query, "filter"):
        query = query.filter(Notification.user_id == user_id)
        filters = filters or {}
        module = module or filters.get("module") or filters.get("related_module")
        priority = priority or filters.get("priority")
        is_read = filters.get("is_read", filters.get("read", is_read))
        if module:
            query = query.filter(Notification.related_module.ilike(f"%{module}%"))
        if priority:
            query = query.filter(Notification.priority == priority.upper())
        if is_read is not None:
            query = query.filter(Notification.is_read == is_read)
    if hasattr(query, "order_by"):
        query = query.order_by(Notification.created_at.desc())
    if hasattr(query, "all"):
        try:
            return query.all()
        except Exception:
            # The deployed DB can be one migration behind the ORM.  Reflect
            # its actual columns so existing notifications remain readable.
            db.rollback()
            return _legacy_notification_rows(db, user_id, module, priority, is_read)
    return []


def get_unread_notifications(db: Session, user_id: int) -> List[Notification]:
    """Return current user's unread notifications."""
    if db is None or Notification is None:
        return []
    query = db.query(Notification)
    if hasattr(query, "filter"):
        query = query.filter(Notification.user_id == user_id, Notification.is_read == False)
    if hasattr(query, "order_by"):
        query = query.order_by(Notification.created_at.desc())
    try:
        return query.all() if hasattr(query, "all") else []
    except Exception:
        db.rollback()
        return _legacy_notification_rows(db, user_id, None, None, False)


def mark_notification_as_read(db: Session, notification_id: int, user_id: int) -> Optional[Notification]:
    """Mark owned notification as read with timestamp."""
    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.user_id == user_id)
        .first()
    )
    if not notification:
        return None

    notification.is_read = True
    notification.read_at = datetime.utcnow()
    db.commit()
    db.refresh(notification)
    return notification


def mark_notification_read(db: Session, notification_id: int, user_id: int) -> Optional[Notification]:
    """Backward-compatible alias used by Module 9 service consumers."""
    return mark_notification_as_read(db, notification_id, user_id)


def mark_all_notifications_read(db: Session, user_id: int) -> int:
    return mark_all_user_notifications_as_read(db, user_id)


def mark_all_user_notifications_as_read(db: Session, user_id: int) -> int:
    """Mark all unread notifications for a user as read."""
    unread = get_unread_notifications(db, user_id)
    now = datetime.utcnow()
    count = 0
    for notif in unread:
        notif.is_read = True
        notif.read_at = now
        count += 1
    if count > 0:
        db.commit()
    return count


def send_email_notification(
    to_email: str,
    subject: str,
    body: str,
    user_id: Optional[int] = None
) -> Dict[str, Any]:
    """Send email only when the complete SMTP configuration is present."""
    host = os.getenv("SMTP_HOST")
    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("SMTP_FROM") or username
    if not all((host, username, password, sender)):
        return {
        "status": "not_configured",
        "channel": "email",
        "to_email": to_email,
        "subject": subject,
        "dispatched_at": datetime.utcnow().isoformat()
        }

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = to_email
    message.set_content(body)
    try:
        with smtplib.SMTP(host, int(os.getenv("SMTP_PORT", "587")), timeout=10) as client:
            if os.getenv("SMTP_USE_TLS", "true").lower() not in {"0", "false", "no"}:
                client.starttls()
            client.login(username, password)
            client.send_message(message)
    except (OSError, smtplib.SMTPException) as exc:
        return {"status": "failed", "channel": "email", "to_email": to_email, "error": str(exc)}
    return {"status": "sent", "channel": "email", "to_email": to_email, "dispatched_at": datetime.utcnow().isoformat()}


def send_sms_notification(
    phone_number: str,
    message: str,
    user_id: Optional[int] = None
) -> Dict[str, Any]:
    """Send SMS through Twilio only when its credentials are complete."""
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    sender = os.getenv("TWILIO_FROM_NUMBER")
    if not all((account_sid, auth_token, sender)):
        return {
        "status": "not_configured",
        "channel": "sms",
        "to_phone": phone_number,
        "message": message,
        "dispatched_at": datetime.utcnow().isoformat()
        }
    encoded = urlencode({"To": phone_number, "From": sender, "Body": message}).encode()
    credentials = base64.b64encode(f"{account_sid}:{auth_token}".encode()).decode()
    request = Request(
        f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json",
        data=encoded,
        headers={"Authorization": f"Basic {credentials}", "Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=10):
            pass
    except (OSError, URLError) as exc:
        return {"status": "failed", "channel": "sms", "to_phone": phone_number, "error": str(exc)}
    return {"status": "sent", "channel": "sms", "to_phone": phone_number, "dispatched_at": datetime.utcnow().isoformat()}


def create_notification(
    db: Session,
    user_id: int,
    title: str,
    message: str,
    notification_type: str = "INFO",
    priority: str = "MEDIUM",
    delivery_method: str = "IN_APP",
    related_module: Optional[str] = None,
    related_record_id: Optional[int] = None,
    vendor_id: Optional[int] = None,
    contract_id: Optional[int] = None,
    purchase_order_id: Optional[int] = None,
    procurement_request_id: Optional[int] = None,
    link: Optional[str] = None,
    related_entity_id: Optional[int] = None  # Backward compatibility parameter
) -> Notification:
    """Factory method to persist notifications and dispatch optional external Email/SMS."""
    rec_id = related_record_id or related_entity_id or contract_id or purchase_order_id or procurement_request_id or vendor_id

    notification = Notification(
        user_id=user_id,
        vendor_id=vendor_id,
        contract_id=contract_id,
        purchase_order_id=purchase_order_id,
        procurement_request_id=procurement_request_id,
        title=title,
        message=message,
        type=notification_type,
        notification_type=notification_type,
        related_module=related_module or "Procurement",
        related_record_id=rec_id,
        priority=priority.upper(),
        delivery_method=delivery_method.upper(),
        is_read=False,
        link=link
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)

    # Trigger external notifications if configured
    target_user = db.query(User).filter(User.id == user_id).first()
    if target_user:
        if delivery_method.upper() in ["EMAIL", "ALL"] and target_user.email:
            send_email_notification(to_email=target_user.email, subject=title, body=message, user_id=user_id)
        phone = getattr(target_user, "mobile_number", None) or getattr(target_user, "phone", None)
        if delivery_method.upper() in ["SMS", "ALL"] and phone:
            send_sms_notification(phone_number=phone, message=f"{title}: {message}", user_id=user_id)

    return notification


# --- Specialized Event Trigger Helpers ---

def _event_recipient_ids(db: Session, vendor_id: Optional[int] = None, owner_id: Optional[int] = None) -> list[int]:
    """Return every active Admin/Procurement Manager plus owner and vendor user.

    Role membership is intentionally resolved in Python: this keeps the rule
    explicit and works consistently with legacy databases that store role text.
    """
    users = list(db.query(User).all() or [])
    recipient_ids = {
        getattr(user, "id", None) for user in users
        if getattr(user, "id", None) is not None
        and getattr(user, "is_active", True)
        and str(getattr(user, "role", "")).strip().lower() in {"administrator", "admin", "procurement manager"}
    }
    if owner_id:
        recipient_ids.add(owner_id)
    if vendor_id:
        vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
        vendor_email = getattr(vendor, "email", None)
        recipient_ids.update(getattr(user, "id", None) for user in users
                             if getattr(user, "id", None) is not None
                             and (getattr(user, "email", None) == vendor_email
                                  or (str(getattr(user, "role", "")).lower() == "vendor"
                                      and getattr(user, "company_name", None) == getattr(vendor, "company_name", None))))
    return sorted(recipient_ids)


def _linked_vendor_user_ids(db: Session, vendor_id: int) -> list[int]:
    """Return active user accounts explicitly linked to the vendor email."""
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        return []
    return [
        user.id for user in db.query(User).all() or []
        if getattr(user, "id", None) is not None
        and getattr(user, "is_active", True)
        and getattr(user, "email", None) == getattr(vendor, "email", None)
    ]


def _owner_recipient_ids(db: Session, vendor_id: int, owner_id: Optional[int] = None) -> list[int]:
    """Target record owners: the linked vendor account and an explicit manager."""
    recipients = set(_linked_vendor_user_ids(db, vendor_id))
    if owner_id:
        recipients.add(owner_id)
    return sorted(recipients)


def _notification_exists_for_today(
    db: Session, *, user_id: int, notification_type: str, related_record_id: int
) -> bool:
    """Check idempotency at the recipient + event-record level."""
    start_of_today = datetime.combine(date.today(), datetime.min.time())
    return db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.notification_type == notification_type,
        Notification.related_record_id == related_record_id,
        Notification.created_at >= start_of_today,
    ).first() is not None

def create_vendor_approval_notification(db: Session, vendor_id: int, approved: bool) -> List[Notification]:
    """Generate approval / rejection notifications when vendor status updates."""
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        return []

    title = "Vendor Approval Confirmed" if approved else "Vendor Registration Status Update"
    msg = f"Your vendor account '{vendor.company_name}' has been approved." if approved else f"Your vendor account '{vendor.company_name}' registration requires additional document verification."
    priority = "MEDIUM" if approved else "HIGH"

    notification_type = "VENDOR_APPROVAL" if approved else "VENDOR_REJECTION"
    notifications = []
    for user_id in _linked_vendor_user_ids(db, vendor_id):
        if not _notification_exists_for_today(db, user_id=user_id, notification_type=notification_type, related_record_id=vendor_id):
            notifications.append(create_notification(
                db=db, user_id=user_id, vendor_id=vendor_id, title=title, message=msg,
                notification_type=notification_type, priority=priority, delivery_method="ALL",
                related_module="Vendor", related_record_id=vendor_id, link=f"/vendors/{vendor_id}",
            ))
    return notifications


def create_procurement_alert(
    db: Session,
    user_id: int,
    pr_id: int,
    status: str,
    pr_title: Optional[str] = None
) -> Notification:
    """Generate alerts for procurement request submissions or approvals."""
    priority = "HIGH" if status.lower() in ["approval_required", "urgent"] else "MEDIUM"
    return create_notification(
        db=db,
        user_id=user_id,
        procurement_request_id=pr_id,
        title=f"Procurement Request: {status.upper()}",
        message=f"Procurement request #{pr_id} ('{pr_title or 'Request'}') status updated to {status}.",
        notification_type="PROCUREMENT_ALERT",
        priority=priority,
        delivery_method="IN_APP",
        related_module="Procurement",
        related_record_id=pr_id,
        link=f"/procurement/requests/{pr_id}"
    )


def create_delivery_delay_notification(db: Session, po_id: int) -> List[Notification]:
    """Trigger alerts when a purchase order delivery is delayed past deadline."""
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        return []

    notifications = []
    for user_id in _owner_recipient_ids(db, po.vendor_id, getattr(po, "assigned_procurement_manager_id", None)):
        if _notification_exists_for_today(db, user_id=user_id, notification_type="DELIVERY_DELAY", related_record_id=po_id):
            continue
        notif = create_notification(
            db=db,
            user_id=user_id,
            purchase_order_id=po_id,
            vendor_id=po.vendor_id,
            title="DELIVERY DELAY WARNING",
            message=f"Purchase Order #{po_id} delivery has passed expected date.",
            notification_type="DELIVERY_DELAY",
            priority="HIGH",
            delivery_method="ALL",
            related_module="Procurement",
            related_record_id=po_id,
            link=f"/procurement/purchase-orders/{po_id}"
        )
        notifications.append(notif)
    return notifications


def trigger_contract_expiry_reminders(db: Session) -> int:
    """Background check for contracts expiring at 90, 30, 7, or 1 day thresholds."""
    today = date.today()
    contracts = db.query(Contract).all()
    created_count = 0

    for contract in contracts:
        if not contract.end_date:
            continue

        end = contract.end_date.date() if isinstance(contract.end_date, datetime) else contract.end_date
        days_left = (end - today).days

        contract_status = str(getattr(contract, "status", "Active")).strip().casefold()
        if days_left in [90, 30, 7, 1] and contract_status not in {"cancelled", "terminated", "expired"}:
            for user_id in _owner_recipient_ids(db, contract.vendor_id, getattr(contract, "responsible_manager_id", None)):
                if _notification_exists_for_today(db, user_id=user_id, notification_type="CONTRACT_EXPIRY", related_record_id=contract.id):
                    continue
                create_notification(
                    db=db,
                    user_id=user_id,
                    contract_id=contract.id,
                    vendor_id=contract.vendor_id,
                    title="CONTRACT EXPIRY REMINDER",
                    message=f"Contract '{contract.contract_title or contract.contract_number}' expires in {days_left} days.",
                    notification_type="CONTRACT_EXPIRY",
                    priority="HIGH" if days_left <= 7 else "MEDIUM",
                    delivery_method="ALL",
                    related_module="Contracts",
                    related_record_id=contract.id,
                    link="/contracts"
                )
                created_count += 1

    return created_count


def trigger_compliance_expiry_reminders(db: Session) -> int:
    """Background check for compliance certifications expiring within 30 days."""
    today = date.today()
    certifications = db.query(Certification).all()
    created_count = 0

    for cert in certifications:
        if not cert.expiry_date:
            continue

        exp = cert.expiry_date.date() if isinstance(cert.expiry_date, datetime) else cert.expiry_date
        days_left = (exp - today).days

        if 0 <= days_left <= 30:
            for user_id in _owner_recipient_ids(db, cert.vendor_id):
                if _notification_exists_for_today(db, user_id=user_id, notification_type="COMPLIANCE_ALERT", related_record_id=cert.id):
                    continue
                create_notification(
                    db=db,
                    user_id=user_id,
                    vendor_id=cert.vendor_id,
                    title="COMPLIANCE CERTIFICATE EXPIRY",
                    message=f"Certification '{cert.certification_name}' for vendor #{cert.vendor_id} expires in {days_left} days.",
                    notification_type="COMPLIANCE_ALERT",
                    priority="HIGH" if days_left <= 7 else "MEDIUM",
                    delivery_method="IN_APP",
                    related_module="Compliance",
                    related_record_id=cert.id,
                    link="/compliance"
                )
                created_count += 1

    return created_count


def execute_all_background_notification_checks(db: Session) -> Dict[str, Any]:
    """Automated monitor scanner for contract expiry, delivery delays, and compliance alerts."""
    contract_alerts = trigger_contract_expiry_reminders(db)
    compliance_alerts = trigger_compliance_expiry_reminders(db)

    # Delivery delay scan
    overdue_pos = db.query(PurchaseOrder).all()
    today = date.today()
    delivery_alerts = 0

    for po in overdue_pos:
        exp_date = getattr(po, "expected_delivery_date", None)
        if exp_date:
            d_val = exp_date.date() if isinstance(exp_date, datetime) else exp_date
            if d_val < today and getattr(po, "po_status", "").lower() not in ["completed", "fulfilled", "delivered", "cancelled"]:
                delivery_alerts += len(create_delivery_delay_notification(db, po.id))

    return {
        "status": "success",
        "contract_expiry_alerts_generated": contract_alerts,
        "delivery_delay_alerts_generated": delivery_alerts,
        "compliance_expiry_alerts_generated": compliance_alerts
    }
