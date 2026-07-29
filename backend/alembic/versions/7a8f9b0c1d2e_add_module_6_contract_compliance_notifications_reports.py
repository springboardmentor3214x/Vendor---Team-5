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


def upgrade() -> None:
    # 1. Contract Renewals table
    op.create_table(
        'contract_renewals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('contract_id', sa.Integer(), nullable=False),
        sa.Column('previous_end_date', sa.DateTime(), nullable=False),
        sa.Column('new_end_date', sa.DateTime(), nullable=False),
        sa.Column('renewal_date', sa.DateTime(), nullable=True),
        sa.Column('renewed_by', sa.Integer(), nullable=True),
        sa.Column('renewal_notes', sa.Text(), nullable=True),
        sa.Column('revised_contract_value', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['contract_id'], ['contracts.id'], ),
        sa.ForeignKeyConstraint(['renewed_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contract_renewals_contract_id'), 'contract_renewals', ['contract_id'], unique=False)
    op.create_index(op.f('ix_contract_renewals_id'), 'contract_renewals', ['id'], unique=False)
    op.create_index(op.f('ix_contract_renewals_renewed_by'), 'contract_renewals', ['renewed_by'], unique=False)

    # 2. Vendor Certifications table
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
    op.create_table(
        'compliance_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vendor_id', sa.Integer(), nullable=False),
        sa.Column('contract_id', sa.Integer(), nullable=True),
        sa.Column('compliance_type', sa.String(length=100), nullable=False),
        sa.Column('compliance_status', sa.String(length=50), nullable=True),
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

    # 4. Notifications table
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
    with op.batch_alter_table('contracts') as batch_op:
        batch_op.add_column(sa.Column('contract_number', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('procurement_request_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('procurement_category', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('payment_terms', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('sla_details', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('warranty_details', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('responsible_manager_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('signed_document_path', sa.String(length=500), nullable=True))
        batch_op.create_index('ix_contracts_contract_number', ['contract_number'], unique=True)
        batch_op.create_index('ix_contracts_vendor_id', ['vendor_id'], unique=False)
        batch_op.create_index('ix_contracts_end_date', ['end_date'], unique=False)
        batch_op.create_index('ix_contracts_status', ['status'], unique=False)
        batch_op.create_index('ix_contracts_created_at', ['created_at'], unique=False)
        batch_op.create_foreign_key('fk_contracts_procurement_request', 'procurement_requests', ['procurement_request_id'], ['id'])
        batch_op.create_foreign_key('fk_contracts_responsible_manager', 'users', ['responsible_manager_id'], ['id'])


def downgrade() -> None:
    with op.batch_alter_table('contracts') as batch_op:
        batch_op.drop_constraint('fk_contracts_responsible_manager', type_='foreignkey')
        batch_op.drop_constraint('fk_contracts_procurement_request', type_='foreignkey')
        batch_op.drop_index('ix_contracts_created_at')
        batch_op.drop_index('ix_contracts_status')
        batch_op.drop_index('ix_contracts_end_date')
        batch_op.drop_index('ix_contracts_vendor_id')
        batch_op.drop_index('ix_contracts_contract_number')
        batch_op.drop_column('signed_document_path')
        batch_op.drop_column('responsible_manager_id')
        batch_op.drop_column('warranty_details')
        batch_op.drop_column('sla_details')
        batch_op.drop_column('payment_terms')
        batch_op.drop_column('procurement_category')
        batch_op.drop_column('procurement_request_id')
        batch_op.drop_column('contract_number')

    op.drop_index(op.f('ix_report_logs_user_id'), table_name='report_logs')
    op.drop_index(op.f('ix_report_logs_id'), table_name='report_logs')
    op.drop_index(op.f('ix_report_logs_created_at'), table_name='report_logs')
    op.drop_table('report_logs')

    op.drop_index(op.f('ix_notifications_vendor_id'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_user_id'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_type'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_is_read'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_id'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_created_at'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_contract_id'), table_name='notifications')
    op.drop_table('notifications')

    op.drop_index(op.f('ix_compliance_records_verified_by'), table_name='compliance_records')
    op.drop_index(op.f('ix_compliance_records_vendor_id'), table_name='compliance_records')
    op.drop_index(op.f('ix_compliance_records_id'), table_name='compliance_records')
    op.drop_index(op.f('ix_compliance_records_created_at'), table_name='compliance_records')
    op.drop_index(op.f('ix_compliance_records_contract_id'), table_name='compliance_records')
    op.drop_index(op.f('ix_compliance_records_compliance_status'), table_name='compliance_records')
    op.drop_table('compliance_records')

    op.drop_index(op.f('ix_vendor_certifications_vendor_id'), table_name='vendor_certifications')
    op.drop_index(op.f('ix_vendor_certifications_uploaded_by'), table_name='vendor_certifications')
    op.drop_index(op.f('ix_vendor_certifications_status'), table_name='vendor_certifications')
    op.drop_index(op.f('ix_vendor_certifications_id'), table_name='vendor_certifications')
    op.drop_index(op.f('ix_vendor_certifications_expiry_date'), table_name='vendor_certifications')
    op.drop_index(op.f('ix_vendor_certifications_created_at'), table_name='vendor_certifications')
    op.drop_table('vendor_certifications')

    op.drop_index(op.f('ix_contract_renewals_renewed_by'), table_name='contract_renewals')
    op.drop_index(op.f('ix_contract_renewals_id'), table_name='contract_renewals')
    op.drop_index(op.f('ix_contract_renewals_contract_id'), table_name='contract_renewals')
    op.drop_table('contract_renewals')
