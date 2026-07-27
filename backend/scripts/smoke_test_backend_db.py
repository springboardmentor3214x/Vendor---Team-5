"""Verify that the configured VendorIQ database is reachable and usable."""
from __future__ import annotations

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

REQUESTED_TABLES = (
    "users", "vendors", "procurement_requests", "purchase_orders", "invoices",
    "performance_records", "delivery_performance", "product_quality_evaluations",
    "communication_logs", "service_ratings", "vendor_rankings",
)


def main() -> int:
    db = None
    try:
        # Import here so a missing PostgreSQL driver is reported as a useful
        # smoke-test failure rather than an unhandled startup traceback.
        from app.core.database import Base, SessionLocal
        import app.models  # noqa: F401 - registers models with Base.metadata

        db = SessionLocal()
        db.execute(text("SELECT 1"))
        print("DATABASE CONNECTION: SUCCESS")
        existing = set(inspect(db.bind).get_table_names())
        model_tables = set(Base.metadata.tables)
        print("\nTABLE CHECK:")
        for table in REQUESTED_TABLES:
            if table in existing:
                count = db.execute(text(f'SELECT COUNT(*) FROM "{table}"')).scalar_one()
                print(f"  FOUND   {table}: {count} row(s)")
            elif table in model_tables:
                print(f"  MISSING {table}: model exists; run `alembic upgrade head`")
            else:
                print(f"  SKIPPED {table}: no SQLAlchemy model is currently defined")
        missing = sorted(model_tables - existing)
        if missing:
            print("\nDATABASE SMOKE TEST: ERROR")
            print("Model tables missing: " + ", ".join(missing))
            print("Run `alembic upgrade head` and try again.")
            return 1
        print("\nDATABASE SMOKE TEST: SUCCESS")
        return 0
    except (SQLAlchemyError, ImportError, ModuleNotFoundError) as exc:
        print("DATABASE CONNECTION: FAILED")
        print(f"{exc.__class__.__name__}: {exc}")
        print("Check PostgreSQL is running, vendor_db exists, and DATABASE_URL is set in backend/.env.")
        return 1
    finally:
        if db is not None:
            db.close()


if __name__ == "__main__":
    raise SystemExit(main())
