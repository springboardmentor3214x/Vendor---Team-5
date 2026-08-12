"""Application-lifecycle scheduler for the existing Module 9 scan helpers.

The scheduler intentionally delegates all notification decisions to
``notification_service``.  It owns only lifecycle/session management, so
business rules remain in the service layer.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Optional

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings
from app.core.database import SessionLocal
from app.services import notification_service

logger = logging.getLogger(__name__)


def run_notification_scan_job() -> dict[str, Any]:
    """Run all existing notification scans using an isolated DB session."""
    db = SessionLocal()
    try:
        result = notification_service.execute_all_background_notification_checks(db)
        logger.info("Completed scheduled notification scan: %s", result)
        return result
    except Exception:
        logger.exception("Scheduled notification scan failed")
        raise
    finally:
        db.close()


def create_notification_scheduler(*, force: bool = False) -> Optional[BackgroundScheduler]:
    """Create and start the configured recurring scan scheduler, if enabled."""
    # FastAPI TestClient runs the lifespan hook.  Never let an application
    # test mutate a developer's configured database through background jobs;
    # focused scheduler tests opt in with ``force=True``.
    if not force and os.getenv("PYTEST_CURRENT_TEST"):
        logger.info("Notification scheduler is disabled during pytest")
        return None

    if not settings.NOTIFICATION_SCHEDULER_ENABLED:
        logger.info("Notification scheduler is disabled by configuration")
        return None

    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(
        run_notification_scan_job,
        trigger="interval",
        minutes=max(1, settings.NOTIFICATION_SCHEDULER_INTERVAL_MINUTES),
        id="module9_notification_scans",
        replace_existing=True,
        coalesce=True,
        max_instances=1,
    )
    scheduler.start()
    logger.info(
        "Notification scheduler started; scan interval=%s minute(s)",
        settings.NOTIFICATION_SCHEDULER_INTERVAL_MINUTES,
    )
    return scheduler


def stop_notification_scheduler(scheduler: Optional[BackgroundScheduler]) -> None:
    """Stop a scheduler created by :func:`create_notification_scheduler`."""
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Notification scheduler stopped")
