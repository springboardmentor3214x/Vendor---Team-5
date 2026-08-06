"""add module 5 and 6 consolidated fields and parity checks

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-30 18:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def get_fresh_inspector():
    conn = op.get_bind()
    return sa.inspect(conn)


def upgrade() -> None:
    inspector = get_fresh_inspector()

    # 1. performance_records: add average_communication_score
    if inspector.has_table('performance_records'):
        pr_cols = [c['name'] for c in inspector.get_columns('performance_records')]
        with op.batch_alter_table('performance_records') as batch_op:
            if 'average_communication_score' not in pr_cols:
                batch_op.add_column(sa.Column('average_communication_score', sa.Float(), nullable=True, server_default='0.0'))
        op.execute("UPDATE performance_records SET average_communication_score = 0.0 WHERE average_communication_score IS NULL")

    # 2. vendor_reliability: add procurement_history_score and verify Module 5 columns
    if not inspector.has_table('vendor_reliability'):
        op.create_table(
            'vendor_reliability',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('vendor_id', sa.Integer(), nullable=False),
            sa.Column('delivery_score', sa.Float(), nullable=True, server_default='0.0'),
            sa.Column('quality_score', sa.Float(), nullable=True, server_default='0.0'),
            sa.Column('communication_score', sa.Float(), nullable=True, server_default='0.0'),
            sa.Column('compliance_score', sa.Float(), nullable=True, server_default='0.0'),
            sa.Column('issue_resolution_score', sa.Float(), nullable=True, server_default='0.0'),
            sa.Column('procurement_history_score', sa.Float(), nullable=True, server_default='0.0'),
            sa.Column('reliability_score', sa.Float(), nullable=True, server_default='0.0'),
            sa.Column('risk_level', sa.String(length=50), nullable=True, server_default='Medium'),
            sa.Column('recommendation', sa.String(length=500), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id']),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_vendor_reliability_id'), 'vendor_reliability', ['id'], unique=False)
        op.create_index(op.f('ix_vendor_reliability_risk_level'), 'vendor_reliability', ['risk_level'], unique=False)
        op.create_index(op.f('ix_vendor_reliability_vendor_id'), 'vendor_reliability', ['vendor_id'], unique=True)
    else:
        vr_cols = [c['name'] for c in inspector.get_columns('vendor_reliability')]
        with op.batch_alter_table('vendor_reliability') as batch_op:
            if 'procurement_history_score' not in vr_cols:
                batch_op.add_column(sa.Column('procurement_history_score', sa.Float(), nullable=True, server_default='0.0'))
            if 'delivery_score' not in vr_cols:
                batch_op.add_column(sa.Column('delivery_score', sa.Float(), nullable=True, server_default='0.0'))
            if 'quality_score' not in vr_cols:
                batch_op.add_column(sa.Column('quality_score', sa.Float(), nullable=True, server_default='0.0'))
            if 'communication_score' not in vr_cols:
                batch_op.add_column(sa.Column('communication_score', sa.Float(), nullable=True, server_default='0.0'))
            if 'compliance_score' not in vr_cols:
                batch_op.add_column(sa.Column('compliance_score', sa.Float(), nullable=True, server_default='0.0'))
            if 'issue_resolution_score' not in vr_cols:
                batch_op.add_column(sa.Column('issue_resolution_score', sa.Float(), nullable=True, server_default='0.0'))
            if 'reliability_score' not in vr_cols:
                batch_op.add_column(sa.Column('reliability_score', sa.Float(), nullable=True, server_default='0.0'))
            if 'risk_level' not in vr_cols:
                batch_op.add_column(sa.Column('risk_level', sa.String(length=50), nullable=True, server_default='Medium'))
            if 'recommendation' not in vr_cols:
                batch_op.add_column(sa.Column('recommendation', sa.String(length=500), nullable=True))
            if 'updated_at' not in vr_cols:
                batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=True))
        op.execute("UPDATE vendor_reliability SET procurement_history_score = 0.0 WHERE procurement_history_score IS NULL")

    # 3. performance_trends: add procurement_history_score and verify trend columns
    if not inspector.has_table('performance_trends'):
        op.create_table(
            'performance_trends',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('vendor_id', sa.Integer(), nullable=False),
            sa.Column('year', sa.Integer(), nullable=False),
            sa.Column('month', sa.Integer(), nullable=False),
            sa.Column('reliability_score', sa.Float(), nullable=True, server_default='0.0'),
            sa.Column('delivery_score', sa.Float(), nullable=True, server_default='0.0'),
            sa.Column('quality_score', sa.Float(), nullable=True, server_default='0.0'),
            sa.Column('communication_score', sa.Float(), nullable=True, server_default='0.0'),
            sa.Column('compliance_score', sa.Float(), nullable=True, server_default='0.0'),
            sa.Column('issue_resolution_score', sa.Float(), nullable=True, server_default='0.0'),
            sa.Column('procurement_history_score', sa.Float(), nullable=True, server_default='0.0'),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id']),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_performance_trends_id'), 'performance_trends', ['id'], unique=False)
        op.create_index(op.f('ix_performance_trends_vendor_id'), 'performance_trends', ['vendor_id'], unique=False)
    else:
        pt_cols = [c['name'] for c in inspector.get_columns('performance_trends')]
        with op.batch_alter_table('performance_trends') as batch_op:
            if 'procurement_history_score' not in pt_cols:
                batch_op.add_column(sa.Column('procurement_history_score', sa.Float(), nullable=True, server_default='0.0'))
            if 'reliability_score' not in pt_cols:
                batch_op.add_column(sa.Column('reliability_score', sa.Float(), nullable=True, server_default='0.0'))
            if 'delivery_score' not in pt_cols:
                batch_op.add_column(sa.Column('delivery_score', sa.Float(), nullable=True, server_default='0.0'))
            if 'quality_score' not in pt_cols:
                batch_op.add_column(sa.Column('quality_score', sa.Float(), nullable=True, server_default='0.0'))
            if 'communication_score' not in pt_cols:
                batch_op.add_column(sa.Column('communication_score', sa.Float(), nullable=True, server_default='0.0'))
            if 'compliance_score' not in pt_cols:
                batch_op.add_column(sa.Column('compliance_score', sa.Float(), nullable=True, server_default='0.0'))
            if 'issue_resolution_score' not in pt_cols:
                batch_op.add_column(sa.Column('issue_resolution_score', sa.Float(), nullable=True, server_default='0.0'))
        op.execute("UPDATE performance_trends SET procurement_history_score = 0.0 WHERE procurement_history_score IS NULL")

    # 4. certifications: ensure certifications table exists for Certification model parity
    if not inspector.has_table('certifications'):
        op.create_table(
            'certifications',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('vendor_id', sa.Integer(), nullable=False),
            sa.Column('certification_name', sa.String(length=255), nullable=False),
            sa.Column('certificate_number', sa.String(length=100), nullable=False),
            sa.Column('issuing_authority', sa.String(length=255), nullable=True),
            sa.Column('issue_date', sa.DateTime(), nullable=False),
            sa.Column('expiry_date', sa.DateTime(), nullable=False),
            sa.Column('document_url', sa.String(length=500), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id']),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_certifications_expiry_date'), 'certifications', ['expiry_date'], unique=False)
        op.create_index(op.f('ix_certifications_id'), 'certifications', ['id'], unique=False)
        op.create_index(op.f('ix_certifications_vendor_id'), 'certifications', ['vendor_id'], unique=False)

    # 5. contracts: parity check
    if inspector.has_table('contracts'):
        c_cols = [c['name'] for c in inspector.get_columns('contracts')]
        with op.batch_alter_table('contracts') as batch_op:
            if 'contract_number' not in c_cols:
                batch_op.add_column(sa.Column('contract_number', sa.String(length=100), nullable=True))
            if 'contract_type' not in c_cols:
                batch_op.add_column(sa.Column('contract_type', sa.String(length=100), nullable=True))
            if 'procurement_category' not in c_cols:
                batch_op.add_column(sa.Column('procurement_category', sa.String(length=100), nullable=True))
            if 'payment_terms' not in c_cols:
                batch_op.add_column(sa.Column('payment_terms', sa.String(length=255), nullable=True))
            if 'sla_details' not in c_cols:
                batch_op.add_column(sa.Column('sla_details', sa.Text(), nullable=True))
            if 'sla' not in c_cols:
                batch_op.add_column(sa.Column('sla', sa.String(length=500), nullable=True))
            if 'warranty_details' not in c_cols:
                batch_op.add_column(sa.Column('warranty_details', sa.Text(), nullable=True))
            if 'responsible_manager' not in c_cols:
                batch_op.add_column(sa.Column('responsible_manager', sa.String(length=255), nullable=True))
            if 'document_url' not in c_cols:
                batch_op.add_column(sa.Column('document_url', sa.String(length=500), nullable=True))
            if 'signed_document_path' not in c_cols:
                batch_op.add_column(sa.Column('signed_document_path', sa.String(length=500), nullable=True))
            if 'compliance_verified' not in c_cols:
                batch_op.add_column(sa.Column('compliance_verified', sa.Boolean(), nullable=True, server_default='false'))

    # 6. vendor_documents: parity check
    if inspector.has_table('vendor_documents'):
        vd_cols = [c['name'] for c in inspector.get_columns('vendor_documents')]
        with op.batch_alter_table('vendor_documents') as batch_op:
            if 'content_type' not in vd_cols:
                batch_op.add_column(sa.Column('content_type', sa.String(length=100), nullable=True))
            if 'uploaded_by' not in vd_cols:
                batch_op.add_column(sa.Column('uploaded_by', sa.Integer(), nullable=True))

def downgrade() -> None:
    pass
