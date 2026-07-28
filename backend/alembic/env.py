from logging.config import fileConfig
import sys
import os

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import Base
from app.core.config import settings
from app.models.vendor import Vendor
from app.models.invoice import Invoice
from app.models.communication import Communication
from app.models.vendor_document import VendorDocument
from app.models.vendor_category import VendorCategory
from app.models.vendor_contact import VendorContact
from app.models.contract import Contract
from app.models.contract_document import ContractDocument
from app.models.procurement_request import ProcurementRequest
from app.models.purchase_order import PurchaseOrder
from app.models.performance import PerformanceRecord
from app.models.activity_log import ActivityLog
from app.models.user import User
from app.models.role import Role
from app.models.delivery_performance import DeliveryPerformance
from app.models.product_quality_evaluation import ProductQualityEvaluation
from app.models.communication_log import CommunicationLog
from app.models.service_rating import ServiceRating
from app.models.vendor_ranking import VendorRanking
from app.models.password_reset_token import PasswordResetToken
from app.models.vendor_approval_history import VendorApprovalHistory
from app.models.procurement_approval import ProcurementApproval
from app.models.order_tracking import OrderTracking
from app.models.procurement_status_history import ProcurementStatusHistory
from app.models.reliability import VendorReliability, PerformanceTrend, ProcurementRecommendation

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()