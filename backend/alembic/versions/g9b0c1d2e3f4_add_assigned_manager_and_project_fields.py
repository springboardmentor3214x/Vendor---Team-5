"""add assigned_procurement_manager_id and project_name fields to purchase_orders and procurement_requests

Revision ID: g9b0c1d2e3f4
Revises: f8a9b0c1d2e3
Create Date: 2026-08-06 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = 'g9b0c1d2e3f4'
down_revision = 'f8a9b0c1d2e3'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)
    tables = inspector.get_table_names()

    if 'purchase_orders' in tables:
        cols = [c['name'] for c in inspector.get_columns('purchase_orders')]
        if 'assigned_procurement_manager_id' not in cols:
            op.add_column('purchase_orders', sa.Column('assigned_procurement_manager_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True))
        if 'project_name' not in cols:
            op.add_column('purchase_orders', sa.Column('project_name', sa.String(length=255), nullable=True))

    if 'procurement_requests' in tables:
        cols = [c['name'] for c in inspector.get_columns('procurement_requests')]
        if 'project_name' not in cols:
            op.add_column('procurement_requests', sa.Column('project_name', sa.String(length=255), nullable=True))


def downgrade():
    pass
