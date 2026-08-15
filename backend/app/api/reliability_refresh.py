"""API-layer adapters for post-write reliability refreshes.

Primary workflow writes commit before these helpers run.  A refresh failure must
therefore be observable without falsely reporting that the already-persisted
primary operation failed.  The service layer remains the source of all scoring
and ranking logic.
"""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.services.reliability_service import (
    refresh_vendor_reliability_after_compliance_update,
    refresh_vendor_reliability_after_performance_write,
    refresh_vendor_reliability_after_procurement_update,
)

logger = logging.getLogger(__name__)


def refresh_after_performance_write(vendor_id: int, db: Session) -> None:
    try:
        refresh_vendor_reliability_after_performance_write(vendor_id, db)
    except Exception:
        logger.exception("Reliability refresh failed after performance write for vendor %s", vendor_id)


def refresh_after_procurement_update(vendor_id: int, db: Session) -> None:
    try:
        refresh_vendor_reliability_after_procurement_update(vendor_id, db)
    except Exception:
        logger.exception("Reliability refresh failed after procurement update for vendor %s", vendor_id)


def refresh_after_compliance_update(vendor_id: int, db: Session) -> None:
    try:
        refresh_vendor_reliability_after_compliance_update(vendor_id, db)
    except Exception:
        logger.exception("Reliability refresh failed after compliance update for vendor %s", vendor_id)
