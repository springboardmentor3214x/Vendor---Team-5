"""add Module 9 notification fields for priority delivery method and entity linkages

Revision ID: f8a9b0c1d2e3
Revises: e7f8a9b0c1d2
Create Date: 2026-08-04 20:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = 'f8a9b0c1d2e3'
down_revision = 'e7f8a9b0c1d2'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)
    tables = inspector.get_table_names()

    if 'notifications' in tables:
        cols = [c['name'] for c in inspector.get_columns('notifications')]
        if 'purchase_order_id' not in cols:
            op.add_column('notifications', sa.Column('purchase_order_id', sa.Integer(), sa.ForeignKey('purchase_orders.id'), nullable=True))
        if 'procurement_request_id' not in cols:
            op.add_column('notifications', sa.Column('procurement_request_id', sa.Integer(), sa.ForeignKey('procurement_requests.id'), nullable=True))
        if 'notification_type' not in cols:
            op.add_column('notifications', sa.Column('notification_type', sa.String(length=50), nullable=True, server_default='INFO'))
        if 'related_module' not in cols:
            op.add_column('notifications', sa.Column('related_module', sa.String(length=100), nullable=True))
        if 'related_record_id' not in cols:
            op.add_column('notifications', sa.Column('related_record_id', sa.Integer(), nullable=True))
        if 'priority' not in cols:
            op.add_column('notifications', sa.Column('priority', sa.String(length=20), nullable=True, server_default='MEDIUM'))
        if 'delivery_method' not in cols:
            op.add_column('notifications', sa.Column('delivery_method', sa.String(length=20), nullable=True, server_default='IN_APP'))
        if 'read_at' not in cols:
            op.add_column('notifications', sa.Column('read_at', sa.DateTime(), nullable=True))


def downgrade():
    pass
