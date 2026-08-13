"""add document lifecycle, procurement/invoice supporting documents, and vendor issues tables

Revision ID: k2b3c4d5e6f7
Revises: j1a2b3c4d5e6
Create Date: 2026-08-13 22:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision: str = 'k2b3c4d5e6f7'
down_revision: Union[str, Sequence[str], None] = 'j1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)

    # 1. vendor_documents: add versioning, replacement tracking, file_size
    if inspector.has_table('vendor_documents'):
        vd_cols = [c['name'] for c in inspector.get_columns('vendor_documents')]
        vd_fks = [fk['name'] for fk in inspector.get_foreign_keys('vendor_documents')]
        vd_indexes = [idx['name'] for idx in inspector.get_indexes('vendor_documents')]

        with op.batch_alter_table('vendor_documents') as batch_op:
            if 'file_size' not in vd_cols:
                batch_op.add_column(sa.Column('file_size', sa.Integer(), nullable=True))
            if 'version' not in vd_cols:
                batch_op.add_column(sa.Column('version', sa.Integer(), server_default='1', nullable=False))
            if 'is_current' not in vd_cols:
                batch_op.add_column(sa.Column('is_current', sa.Boolean(), server_default=sa.text('true'), nullable=False))
            if 'replaced_document_id' not in vd_cols:
                batch_op.add_column(sa.Column('replaced_document_id', sa.Integer(), nullable=True))
                if 'fk_vendor_docs_replaced_doc' not in vd_fks:
                    batch_op.create_foreign_key(
                        'fk_vendor_docs_replaced_doc',
                        'vendor_documents',
                        ['replaced_document_id'],
                        ['id']
                    )
            if 'replaced_at' not in vd_cols:
                batch_op.add_column(sa.Column('replaced_at', sa.DateTime(), nullable=True))
            if 'replaced_by' not in vd_cols:
                batch_op.add_column(sa.Column('replaced_by', sa.Integer(), nullable=True))
                if inspector.has_table('users') and 'fk_vendor_docs_replaced_by_users' not in vd_fks:
                    batch_op.create_foreign_key(
                        'fk_vendor_docs_replaced_by_users',
                        'users',
                        ['replaced_by'],
                        ['id']
                    )

    # 2. contract_documents: add content_type, uploaded_by, file_size, versioning & replacement tracking
    if inspector.has_table('contract_documents'):
        cd_cols = [c['name'] for c in inspector.get_columns('contract_documents')]
        cd_fks = [fk['name'] for fk in inspector.get_foreign_keys('contract_documents')]

        with op.batch_alter_table('contract_documents') as batch_op:
            if 'content_type' not in cd_cols:
                batch_op.add_column(sa.Column('content_type', sa.String(length=100), nullable=True))
            if 'uploaded_by' not in cd_cols:
                batch_op.add_column(sa.Column('uploaded_by', sa.Integer(), nullable=True))
                if inspector.has_table('users') and 'fk_contract_docs_uploaded_by_users' not in cd_fks:
                    batch_op.create_foreign_key(
                        'fk_contract_docs_uploaded_by_users',
                        'users',
                        ['uploaded_by'],
                        ['id']
                    )
            if 'file_size' not in cd_cols:
                batch_op.add_column(sa.Column('file_size', sa.Integer(), nullable=True))
            if 'version' not in cd_cols:
                batch_op.add_column(sa.Column('version', sa.Integer(), server_default='1', nullable=False))
            if 'is_current' not in cd_cols:
                batch_op.add_column(sa.Column('is_current', sa.Boolean(), server_default=sa.text('true'), nullable=False))
            if 'replaced_document_id' not in cd_cols:
                batch_op.add_column(sa.Column('replaced_document_id', sa.Integer(), nullable=True))
                if 'fk_contract_docs_replaced_doc' not in cd_fks:
                    batch_op.create_foreign_key(
                        'fk_contract_docs_replaced_doc',
                        'contract_documents',
                        ['replaced_document_id'],
                        ['id']
                    )
            if 'replaced_at' not in cd_cols:
                batch_op.add_column(sa.Column('replaced_at', sa.DateTime(), nullable=True))
            if 'replaced_by' not in cd_cols:
                batch_op.add_column(sa.Column('replaced_by', sa.Integer(), nullable=True))
                if inspector.has_table('users') and 'fk_contract_docs_replaced_by_users' not in cd_fks:
                    batch_op.create_foreign_key(
                        'fk_contract_docs_replaced_by_users',
                        'users',
                        ['replaced_by'],
                        ['id']
                    )

    # 3. procurement_request_documents table
    if not inspector.has_table('procurement_request_documents'):
        op.create_table(
            'procurement_request_documents',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('request_id', sa.Integer(), nullable=False),
            sa.Column('document_type', sa.String(length=100), nullable=False, server_default='Supporting Document'),
            sa.Column('file_name', sa.String(length=255), nullable=False),
            sa.Column('file_path', sa.String(length=500), nullable=False),
            sa.Column('file_size', sa.Integer(), nullable=True),
            sa.Column('content_type', sa.String(length=100), nullable=True),
            sa.Column('uploaded_by', sa.Integer(), nullable=True),
            sa.Column('uploaded_at', sa.DateTime(), nullable=True),
            sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
            sa.Column('is_current', sa.Boolean(), nullable=False, server_default=sa.text('true')),
            sa.Column('replaced_document_id', sa.Integer(), nullable=True),
            sa.Column('replaced_at', sa.DateTime(), nullable=True),
            sa.Column('replaced_by', sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(['request_id'], ['procurement_requests.id']),
            sa.ForeignKeyConstraint(['uploaded_by'], ['users.id']),
            sa.ForeignKeyConstraint(['replaced_by'], ['users.id']),
            sa.ForeignKeyConstraint(['replaced_document_id'], ['procurement_request_documents.id']),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_procurement_request_documents_id'), 'procurement_request_documents', ['id'], unique=False)
        op.create_index(op.f('ix_procurement_request_documents_request_id'), 'procurement_request_documents', ['request_id'], unique=False)

    # 4. invoice_documents table
    if not inspector.has_table('invoice_documents'):
        op.create_table(
            'invoice_documents',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('invoice_id', sa.Integer(), nullable=False),
            sa.Column('document_type', sa.String(length=100), nullable=False, server_default='Invoice Document'),
            sa.Column('file_name', sa.String(length=255), nullable=False),
            sa.Column('file_path', sa.String(length=500), nullable=False),
            sa.Column('file_size', sa.Integer(), nullable=True),
            sa.Column('content_type', sa.String(length=100), nullable=True),
            sa.Column('uploaded_by', sa.Integer(), nullable=True),
            sa.Column('uploaded_at', sa.DateTime(), nullable=True),
            sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
            sa.Column('is_current', sa.Boolean(), nullable=False, server_default=sa.text('true')),
            sa.Column('replaced_document_id', sa.Integer(), nullable=True),
            sa.Column('replaced_at', sa.DateTime(), nullable=True),
            sa.Column('replaced_by', sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id']),
            sa.ForeignKeyConstraint(['uploaded_by'], ['users.id']),
            sa.ForeignKeyConstraint(['replaced_by'], ['users.id']),
            sa.ForeignKeyConstraint(['replaced_document_id'], ['invoice_documents.id']),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_invoice_documents_id'), 'invoice_documents', ['id'], unique=False)
        op.create_index(op.f('ix_invoice_documents_invoice_id'), 'invoice_documents', ['invoice_id'], unique=False)

    # 5. vendor_issues table
    if not inspector.has_table('vendor_issues'):
        op.create_table(
            'vendor_issues',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('vendor_id', sa.Integer(), nullable=False),
            sa.Column('purchase_order_id', sa.Integer(), nullable=True),
            sa.Column('issue_category', sa.String(length=100), nullable=False),
            sa.Column('severity', sa.String(length=50), nullable=False, server_default='Medium'),
            sa.Column('description', sa.String(length=1000), nullable=False),
            sa.Column('status', sa.String(length=50), nullable=False, server_default='Open'),
            sa.Column('reported_by', sa.Integer(), nullable=True),
            sa.Column('reported_date', sa.DateTime(), nullable=False),
            sa.Column('assigned_to', sa.Integer(), nullable=True),
            sa.Column('resolution_notes', sa.String(length=1000), nullable=True),
            sa.Column('resolved_by', sa.Integer(), nullable=True),
            sa.Column('resolved_date', sa.DateTime(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id']),
            sa.ForeignKeyConstraint(['purchase_order_id'], ['purchase_orders.id']),
            sa.ForeignKeyConstraint(['reported_by'], ['users.id']),
            sa.ForeignKeyConstraint(['assigned_to'], ['users.id']),
            sa.ForeignKeyConstraint(['resolved_by'], ['users.id']),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_vendor_issues_id'), 'vendor_issues', ['id'], unique=False)
        op.create_index(op.f('ix_vendor_issues_vendor_id'), 'vendor_issues', ['vendor_id'], unique=False)
        op.create_index(op.f('ix_vendor_issues_purchase_order_id'), 'vendor_issues', ['purchase_order_id'], unique=False)
        op.create_index(op.f('ix_vendor_issues_issue_category'), 'vendor_issues', ['issue_category'], unique=False)
        op.create_index(op.f('ix_vendor_issues_severity'), 'vendor_issues', ['severity'], unique=False)
        op.create_index(op.f('ix_vendor_issues_status'), 'vendor_issues', ['status'], unique=False)
        op.create_index(op.f('ix_vendor_issues_reported_by'), 'vendor_issues', ['reported_by'], unique=False)
        op.create_index(op.f('ix_vendor_issues_assigned_to'), 'vendor_issues', ['assigned_to'], unique=False)


def downgrade() -> None:
    pass
