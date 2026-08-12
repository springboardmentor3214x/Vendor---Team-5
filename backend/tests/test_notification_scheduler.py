"""Focused regression tests for the Module 9 scheduled notification scan."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from types import SimpleNamespace

from app.core import notification_scheduler
from app.models.certification import Certification
from app.models.contract import Contract
from app.models.notification import Notification
from app.models.purchase_order import PurchaseOrder
from app.models.user import User
from app.models.vendor import Vendor
from app.services import notification_service


class _Query:
    def __init__(self, rows):
        self.rows = list(rows)

    def filter(self, *_conditions):
        return self

    def first(self):
        return self.rows[0] if self.rows else None

    def all(self):
        return self.rows


class _SeededScanDb:
    """Small DB double containing one qualifying row for each scan category."""

    def __init__(self):
        today = date.today()
        self.contract = SimpleNamespace(
            id=11,
            vendor_id=7,
            responsible_manager_id=None,
            contract_title="Demo renewal",
            contract_number="CT-DEMO-11",
            end_date=today + timedelta(days=7),
        )
        self.certification = SimpleNamespace(
            id=12,
            vendor_id=7,
            certification_name="ISO Demo",
            expiry_date=today + timedelta(days=14),
        )
        self.purchase_order = SimpleNamespace(
            id=13,
            vendor_id=7,
            assigned_procurement_manager_id=None,
            expected_delivery_date=today - timedelta(days=1),
            po_status="Issued",
        )
        self.admin = SimpleNamespace(
            id=3,
            email="manager@example.test",
            role="Procurement Manager",
            is_active=True,
            company_name=None,
        )
        self.vendor = SimpleNamespace(id=7, email="vendor@example.test", company_name="Demo Supplier")

    def query(self, model):
        if model is Contract:
            return _Query([self.contract])
        if model is Certification:
            return _Query([self.certification])
        if model is PurchaseOrder:
            return _Query([self.purchase_order])
        if model is User:
            return _Query([self.admin])
        if model is Vendor:
            return _Query([self.vendor])
        if model is Notification:
            return _Query([])
        return _Query([])

    def close(self):
        pass


def test_scheduled_scan_generates_contract_compliance_and_delivery_notifications(monkeypatch):
    """The scheduled job must invoke existing helpers for all three seeded risks."""
    db = _SeededScanDb()
    created = []

    def record_notification(**payload):
        created.append(payload)
        return SimpleNamespace(**payload)

    monkeypatch.setattr(notification_service, "create_notification", record_notification)
    monkeypatch.setattr(notification_scheduler, "SessionLocal", lambda: db)

    result = notification_scheduler.run_notification_scan_job()

    assert result["status"] == "success"
    assert result["contract_expiry_alerts_generated"] == 1
    assert result["compliance_expiry_alerts_generated"] == 1
    assert result["delivery_delay_alerts_generated"] == 1
    assert {item["notification_type"] for item in created} == {
        "CONTRACT_EXPIRY",
        "COMPLIANCE_ALERT",
        "DELIVERY_DELAY",
    }


def test_scheduler_job_is_configured_without_running_immediately(monkeypatch):
    """The scheduler registers exactly one recurring job at the configured cadence."""
    class _Scheduler:
        def __init__(self, **_kwargs):
            self.running = False
            self.job = None

        def add_job(self, func, **kwargs):
            self.job = (func, kwargs)

        def start(self):
            self.running = True

        def shutdown(self, wait=False):
            self.running = False

    monkeypatch.setattr(notification_scheduler, "BackgroundScheduler", _Scheduler)
    scheduler = notification_scheduler.create_notification_scheduler(force=True)

    assert scheduler is not None
    assert scheduler.job[0] is notification_scheduler.run_notification_scan_job
    assert scheduler.job[1]["id"] == "module9_notification_scans"
    assert scheduler.job[1]["trigger"] == "interval"
    notification_scheduler.stop_notification_scheduler(scheduler)
