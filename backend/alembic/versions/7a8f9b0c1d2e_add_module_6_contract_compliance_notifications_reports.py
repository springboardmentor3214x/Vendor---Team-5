"""add Module 6 contract compliance notifications reports tables

Revision ID: 7a8f9b0c1d2e
Revises: c2db7eff190a
Create Date: 2026-07-29 19:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a8f9b0c1d2e'
down_revision: Union[str, Sequence[str], None] = 'c2db7eff190a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def get_fresh_inspector():
    conn = op.get_bind()
    return sa.inspect(conn)


def upgrade() -> None:
    inspector = get_fresh_inspector()

    # 1. Contract Renewals table
    if not inspector.has_table('contract_renewals'):
        op.create_table(
            'contract_renewals',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('contract_id', sa.Integer(), nullable=False),
            sa.Column('previous_end_date', sa.DateTime(), nullable=True),
            sa.Column('new_end_date', sa.DateTime(), nullable=False),
            sa.Column('renewal_date', sa.DateTime(), nullable=True),
            sa.Column('renewed_by', sa.Integer(), nullable=True),
            sa.Column('renewal_notes', sa.Text(), nullable=True),
            sa.Column('remarks', sa.String(length=500), nullable=True),
            sa.Column('revised_contract_value', sa.Float(), nullable=True),
            sa.Column('renewal_value', sa.Float(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['contract_id'], ['contracts.id'], ),
            sa.ForeignKeyConstraint(['renewed_by'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_contract_renewals_contract_id'), 'contract_renewals', ['contract_id'], unique=False)
        op.create_index(op.f('ix_contract_renewals_id'), 'contract_renewals', ['id'], unique=False)
        op.create_index(op.f('ix_contract_renewals_renewed_by'), 'contract_renewals', ['renewed_by'], unique=False)

    # 2. Vendor Certifications table
    if not inspector.has_table('vendor_certifications'):
        op.create_table(
            'vendor_certifications',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('vendor_id', sa.Integer(), nullable=False),
            sa.Column('certification_name', sa.String(length=255), nullable=False),
            sa.Column('certificate_number', sa.String(length=100), nullable=True),
            sa.Column('issuing_authority', sa.String(length=255), nullable=True),
            sa.Column('issue_date', sa.DateTime(), nullable=True),
            sa.Column('expiry_date', sa.DateTime(), nullable=True),
            sa.Column('file_name', sa.String(length=255), nullable=True),
            sa.Column('file_path', sa.String(length=500), nullable=True),
            sa.Column('status', sa.String(length=50), nullable=True),
            sa.Column('uploaded_by', sa.Integer(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ),
            sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_vendor_certifications_created_at'), 'vendor_certifications', ['created_at'], unique=False)
        op.create_index(op.f('ix_vendor_certifications_expiry_date'), 'vendor_certifications', ['expiry_date'], unique=False)
        op.create_index(op.f('ix_vendor_certifications_id'), 'vendor_certifications', ['id'], unique=False)
        op.create_index(op.f('ix_vendor_certifications_status'), 'vendor_certifications', ['status'], unique=False)
        op.create_index(op.f('ix_vendor_certifications_uploaded_by'), 'vendor_certifications', ['uploaded_by'], unique=False)
        op.create_index(op.f('ix_vendor_certifications_vendor_id'), 'vendor_certifications', ['vendor_id'], unique=False)

    # 3. Compliance Records table
    if not inspector.has_table('compliance_records'):
        op.create_table(
            'compliance_records',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('vendor_id', sa.Integer(), nullable=False),
            sa.Column('contract_id', sa.Integer(), nullable=True),
            sa.Column('compliance_type', sa.String(length=100), nullable=False),
            sa.Column('compliance_status', sa.String(length=50), nullable=True),
            sa.Column('status', sa.String(length=50), nullable=True),
            sa.Column('verification_date', sa.DateTime(), nullable=True),
            sa.Column('verified_by', sa.Integer(), nullable=True),
            sa.Column('remarks', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['contract_id'], ['contracts.id'], ),
            sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ),
            sa.ForeignKeyConstraint(['verified_by'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_compliance_records_compliance_status'), 'compliance_records', ['compliance_status'], unique=False)
        op.create_index(op.f('ix_compliance_records_contract_id'), 'compliance_records', ['contract_id'], unique=False)
        op.create_index(op.f('ix_compliance_records_created_at'), 'compliance_records', ['created_at'], unique=False)
        op.create_index(op.f('ix_compliance_records_id'), 'compliance_records', ['id'], unique=False)
        op.create_index(op.f('ix_compliance_records_vendor_id'), 'compliance_records', ['vendor_id'], unique=False)
        op.create_index(op.f('ix_compliance_records_verified_by'), 'compliance_records', ['verified_by'], unique=False)
<<<<<<< HEAD
    else:
        cr_cols = [c['name'] for c in inspector.get_columns('compliance_records')]
        cr_indexes = [idx['name'] for idx in inspector.get_indexes('compliance_records')]
        with op.batch_alter_table('compliance_records') as batch_op:
            if 'contract_id' not in cr_cols:
                batch_op.add_column(sa.Column('contract_id', sa.Integer(), nullable=True))
                batch_op.create_foreign_key('fk_compliance_records_contract_id', 'contracts', ['contract_id'], ['id'])
                if 'ix_compliance_records_contract_id' not in cr_indexes:
                    batch_op.create_index('ix_compliance_records_contract_id', ['contract_id'], unique=False)
            if 'compliance_status' not in cr_cols:
                batch_op.add_column(sa.Column('compliance_status', sa.String(length=50), nullable=True))
                if 'ix_compliance_records_compliance_status' not in cr_indexes:
                    batch_op.create_index('ix_compliance_records_compliance_status', ['compliance_status'], unique=False)
            if 'status' not in cr_cols:
                batch_op.add_column(sa.Column('status', sa.String(length=50), nullable=True))
=======
>>>>>>> 5509ac0da30360d3f73d6fd61f4aa23a5127694c

    # 4. Notifications table
    if not inspector.has_table('notifications'):
        op.create_table(
            'notifications',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=True),
            sa.Column('vendor_id', sa.Integer(), nullable=True),
            sa.Column('contract_id', sa.Integer(), nullable=True),
            sa.Column('title', sa.String(length=255), nullable=False),
            sa.Column('message', sa.Text(), nullable=False),
            sa.Column('type', sa.String(length=50), nullable=True),
            sa.Column('is_read', sa.Boolean(), nullable=True),
            sa.Column('link', sa.String(length=500), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['contract_id'], ['contracts.id'], ),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_notifications_contract_id'), 'notifications', ['contract_id'], unique=False)
        op.create_index(op.f('ix_notifications_created_at'), 'notifications', ['created_at'], unique=False)
        op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=False)
        op.create_index(op.f('ix_notifications_is_read'), 'notifications', ['is_read'], unique=False)
        op.create_index(op.f('ix_notifications_type'), 'notifications', ['type'], unique=False)
        op.create_index(op.f('ix_notifications_user_id'), 'notifications', ['user_id'], unique=False)
        op.create_index(op.f('ix_notifications_vendor_id'), 'notifications', ['vendor_id'], unique=False)

    # 5. Report Logs table
    if not inspector.has_table('report_logs'):
        op.create_table(
            'report_logs',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('report_type', sa.String(length=100), nullable=False),
            sa.Column('file_format', sa.String(length=20), nullable=False),
            sa.Column('file_path', sa.String(length=500), nullable=True),
            sa.Column('parameters', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_report_logs_created_at'), 'report_logs', ['created_at'], unique=False)
        op.create_index(op.f('ix_report_logs_id'), 'report_logs', ['id'], unique=False)
        op.create_index(op.f('ix_report_logs_user_id'), 'report_logs', ['user_id'], unique=False)

    # 6. Add columns to contracts table if missing
    if inspector.has_table('contracts'):
        c_cols = [c['name'] for c in inspector.get_columns('contracts')]
        with op.batch_alter_table('contracts') as batch_op:
            if 'contract_number' not in c_cols:
                batch_op.add_column(sa.Column('contract_number', sa.String(length=100), nullable=True))
            if 'procurement_request_id' not in c_cols:
                batch_op.add_column(sa.Column('procurement_request_id', sa.Integer(), nullable=True))
            if 'procurement_category' not in c_cols:
                batch_op.add_column(sa.Column('procurement_category', sa.String(length=100), nullable=True))
            if 'payment_terms' not in c_cols:
                batch_op.add_column(sa.Column('payment_terms', sa.String(length=255), nullable=True))
            if 'sla_details' not in c_cols:
                batch_op.add_column(sa.Column('sla_details', sa.Text(), nullable=True))
            if 'warranty_details' not in c_cols:
                batch_op.add_column(sa.Column('warranty_details', sa.Text(), nullable=True))
            if 'responsible_manager_id' not in c_cols:
                batch_op.add_column(sa.Column('responsible_manager_id', sa.Integer(), nullable=True))
            if 'signed_document_path' not in c_cols:
                batch_op.add_column(sa.Column('signed_document_path', sa.String(length=500), nullable=True))


def downgrade() -> None:
    pass
