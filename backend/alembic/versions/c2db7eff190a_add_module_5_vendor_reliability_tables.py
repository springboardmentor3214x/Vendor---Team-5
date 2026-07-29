"""add Module 5 vendor reliability tables

Revision ID: c2db7eff190a
Revises: 15ba89028e5b
Create Date: 2026-07-28 18:27:58.785335

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c2db7eff190a'
down_revision: Union[str, Sequence[str], None] = '15ba89028e5b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def get_fresh_inspector():
    conn = op.get_bind()
    return sa.inspect(conn)


def upgrade() -> None:
    """Upgrade schema idempotently."""
    inspector = get_fresh_inspector()

    if not inspector.has_table('procurement_recommendations'):
        op.create_table(
            'procurement_recommendations',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('vendor_id', sa.Integer(), nullable=False),
            sa.Column('category_id', sa.Integer(), nullable=True),
            sa.Column('recommendation_score', sa.Float(), nullable=True),
            sa.Column('recommendation_status', sa.String(length=50), nullable=True),
            sa.Column('reason', sa.String(length=500), nullable=True),
            sa.Column('generated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['category_id'], ['vendor_categories.id'], ),
            sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_procurement_recommendations_category_id'), 'procurement_recommendations', ['category_id'], unique=False)
        op.create_index(op.f('ix_procurement_recommendations_generated_at'), 'procurement_recommendations', ['generated_at'], unique=False)
        op.create_index(op.f('ix_procurement_recommendations_id'), 'procurement_recommendations', ['id'], unique=False)
        op.create_index(op.f('ix_procurement_recommendations_recommendation_status'), 'procurement_recommendations', ['recommendation_status'], unique=False)
        op.create_index(op.f('ix_procurement_recommendations_vendor_id'), 'procurement_recommendations', ['vendor_id'], unique=False)

    if not inspector.has_table('procurement_risk_levels'):
        op.create_table(
            'procurement_risk_levels',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('vendor_id', sa.Integer(), nullable=False),
            sa.Column('risk_level', sa.String(length=50), nullable=True),
            sa.Column('risk_reason', sa.String(length=500), nullable=True),
            sa.Column('requires_warning', sa.Integer(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_procurement_risk_levels_id'), 'procurement_risk_levels', ['id'], unique=False)
        op.create_index(op.f('ix_procurement_risk_levels_risk_level'), 'procurement_risk_levels', ['risk_level'], unique=False)
        op.create_index(op.f('ix_procurement_risk_levels_vendor_id'), 'procurement_risk_levels', ['vendor_id'], unique=True)

    if not inspector.has_table('reliability_history'):
        op.create_table(
            'reliability_history',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('vendor_id', sa.Integer(), nullable=False),
            sa.Column('reliability_score', sa.Float(), nullable=True),
            sa.Column('delivery_trend', sa.String(length=50), nullable=True),
            sa.Column('quality_trend', sa.String(length=50), nullable=True),
            sa.Column('communication_trend', sa.String(length=50), nullable=True),
            sa.Column('compliance_trend', sa.String(length=50), nullable=True),
            sa.Column('issue_resolution_trend', sa.String(length=50), nullable=True),
            sa.Column('recorded_month', sa.String(length=20), nullable=True),
            sa.Column('recorded_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_reliability_history_id'), 'reliability_history', ['id'], unique=False)
        op.create_index(op.f('ix_reliability_history_recorded_at'), 'reliability_history', ['recorded_at'], unique=False)
        op.create_index(op.f('ix_reliability_history_vendor_id'), 'reliability_history', ['vendor_id'], unique=False)

    if not inspector.has_table('supplier_reliability_ranking'):
        op.create_table(
            'supplier_reliability_ranking',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('vendor_id', sa.Integer(), nullable=False),
            sa.Column('reliability_score', sa.Float(), nullable=True),
            sa.Column('rank_position', sa.Integer(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_supplier_reliability_ranking_id'), 'supplier_reliability_ranking', ['id'], unique=False)
        op.create_index(op.f('ix_supplier_reliability_ranking_rank_position'), 'supplier_reliability_ranking', ['rank_position'], unique=False)
        op.create_index(op.f('ix_supplier_reliability_ranking_vendor_id'), 'supplier_reliability_ranking', ['vendor_id'], unique=True)

    if not inspector.has_table('vendor_reliability_scores'):
        op.create_table(
            'vendor_reliability_scores',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('vendor_id', sa.Integer(), nullable=False),
            sa.Column('reliability_score', sa.Float(), nullable=True),
            sa.Column('delivery_factor', sa.Float(), nullable=True),
            sa.Column('quality_factor', sa.Float(), nullable=True),
            sa.Column('communication_factor', sa.Float(), nullable=True),
            sa.Column('compliance_factor', sa.Float(), nullable=True),
            sa.Column('purchase_history_factor', sa.Float(), nullable=True),
            sa.Column('issue_resolution_factor', sa.Float(), nullable=True),
            sa.Column('risk_level', sa.String(length=50), nullable=True),
            sa.Column('last_calculated_at', sa.DateTime(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_vendor_reliability_scores_id'), 'vendor_reliability_scores', ['id'], unique=False)
        op.create_index(op.f('ix_vendor_reliability_scores_risk_level'), 'vendor_reliability_scores', ['risk_level'], unique=False)
        op.create_index(op.f('ix_vendor_reliability_scores_vendor_id'), 'vendor_reliability_scores', ['vendor_id'], unique=True)

    if inspector.has_table('invoices'):
        invoices_indexes = [idx['name'] for idx in inspector.get_indexes('invoices')]
        if 'ix_invoices_invoice_number' not in invoices_indexes:
            op.create_index(op.f('ix_invoices_invoice_number'), 'invoices', ['invoice_number'], unique=True)

    if inspector.has_table('procurement_requests'):
        pr_cols = [c['name'] for c in inspector.get_columns('procurement_requests')]
        if 'title' in pr_cols:
            op.alter_column('procurement_requests', 'title', existing_type=sa.VARCHAR(length=255), nullable=False)
        if 'product_name' in pr_cols:
            op.alter_column('procurement_requests', 'product_name', existing_type=sa.VARCHAR(length=255), nullable=False)
        if 'product_category' in pr_cols:
            op.alter_column('procurement_requests', 'product_category', existing_type=sa.VARCHAR(length=100), nullable=False)

        pr_indexes = [idx['name'] for idx in inspector.get_indexes('procurement_requests')]
        if 'ix_procurement_requests_request_number' not in pr_indexes:
            op.create_index(op.f('ix_procurement_requests_request_number'), 'procurement_requests', ['request_number'], unique=True)

    if inspector.has_table('purchase_orders'):
        po_cols = [c['name'] for c in inspector.get_columns('purchase_orders')]
        if 'tax_details' not in po_cols:
            op.add_column('purchase_orders', sa.Column('tax_details', sa.Float(), nullable=True))
        if 'shipping_address' not in po_cols:
            op.add_column('purchase_orders', sa.Column('shipping_address', sa.String(length=500), nullable=True))
        if 'created_by' not in po_cols:
            op.add_column('purchase_orders', sa.Column('created_by', sa.Integer(), nullable=True))
        if 'approved_by' not in po_cols:
            op.add_column('purchase_orders', sa.Column('approved_by', sa.Integer(), nullable=True))
        if 'po_date' not in po_cols:
            op.add_column('purchase_orders', sa.Column('po_date', sa.DateTime(), nullable=True))

    if inspector.has_table('users'):
        user_cols = [c['name'] for c in inspector.get_columns('users')]
        if 'mobile_number' not in user_cols:
            op.add_column('users', sa.Column('mobile_number', sa.String(length=20), nullable=True))
        if 'employee_id' not in user_cols:
            op.add_column('users', sa.Column('employee_id', sa.String(length=50), nullable=True))
        if 'company_name' not in user_cols:
            op.add_column('users', sa.Column('company_name', sa.String(length=255), nullable=True))
        if 'profile_picture_url' not in user_cols:
            op.add_column('users', sa.Column('profile_picture_url', sa.String(length=500), nullable=True))


def downgrade() -> None:
    pass
