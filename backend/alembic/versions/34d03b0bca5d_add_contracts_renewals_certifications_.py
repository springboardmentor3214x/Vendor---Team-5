"""add_contracts_renewals_certifications_compliance

Revision ID: 34d03b0bca5d
Revises: 5694ad64a9c0
Create Date: 2026-07-28 18:59:30.656639

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '34d03b0bca5d'
down_revision: Union[str, Sequence[str], None] = '5694ad64a9c0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# --- Fresh Inspection Helpers ---

def get_fresh_inspector():
    conn = op.get_bind()
    return sa.inspect(conn)


def table_exists(table_name):
    insp = get_fresh_inspector()
    return table_name in insp.get_table_names()


def column_exists(table_name, column_name):
    if not table_exists(table_name):
        return False
    insp = get_fresh_inspector()
    cols = [c['name'] for c in insp.get_columns(table_name)]
    return column_name in cols


def index_exists(table_name, index_name):
    if not table_exists(table_name):
        return False
    insp = get_fresh_inspector()
    indexes = [idx['name'] for idx in insp.get_indexes(table_name)]
    return index_name in indexes


def constraint_exists(table_name, constraint_name, constraint_type='unique'):
    if not table_exists(table_name):
        return False
    insp = get_fresh_inspector()
    if constraint_type == 'unique':
        constraints = [c['name'] for c in insp.get_unique_constraints(table_name)]
    elif constraint_type == 'foreignkey':
        constraints = [c['name'] for c in insp.get_foreign_keys(table_name)]
    elif constraint_type == 'pk':
        pk = insp.get_pk_constraint(table_name)
        return pk and pk.get('name') == constraint_name
    else:
        constraints = []
    return constraint_name in constraints


def fk_exists(source_table, refer_table, source_cols, refer_cols):
    if not table_exists(source_table):
        return False
    insp = get_fresh_inspector()
    fkeys = insp.get_foreign_keys(source_table)
    for fk in fkeys:
        if (fk['constrained_columns'] == source_cols and 
            fk['referred_table'] == refer_table and 
            fk['referred_columns'] == refer_cols):
            return True
    return False


def add_column_if_absent(table_name, column):
    if not column_exists(table_name, column.name):
        op.add_column(table_name, column)


def drop_column_if_present(table_name, column_name):
    if column_exists(table_name, column_name):
        op.drop_column(table_name, column_name)


def create_index_if_absent(index_name, table_name, columns, unique=False):
    if not index_exists(table_name, index_name):
        op.create_index(index_name, table_name, columns, unique=unique)


def drop_index_if_present(index_name, table_name):
    if index_exists(table_name, index_name):
        op.drop_index(index_name, table_name=table_name)


def drop_constraint_if_present(constraint_name, table_name, constraint_type='unique'):
    if constraint_exists(table_name, constraint_name, constraint_type):
        op.drop_constraint(constraint_name, table_name, type_=constraint_type)


def create_fk_if_absent(fk_name, source_table, refer_table, source_cols, refer_cols):
    if not fk_exists(source_table, refer_table, source_cols, refer_cols):
        op.create_foreign_key(fk_name, source_table, refer_table, source_cols, refer_cols)


def drop_fk_if_present(source_table, refer_table, source_cols, refer_cols):
    if not table_exists(source_table):
        return
    insp = get_fresh_inspector()
    fkeys = insp.get_foreign_keys(source_table)
    for fk in fkeys:
        if (fk['constrained_columns'] == source_cols and 
            fk['referred_table'] == refer_table and 
            fk['referred_columns'] == refer_cols):
            if fk.get('name'):
                op.drop_constraint(fk['name'], source_table, type_='foreignkey')
            else:
                op.drop_constraint(None, source_table, type_='foreignkey')


def column_has_nulls(table_name, column_name):
    conn = op.get_bind()
    query = sa.text(f"SELECT COUNT(*) FROM {table_name} WHERE {column_name} IS NULL")
    result = conn.execute(query).scalar()
    return result > 0


# --- Alembic Entry Points ---

def upgrade() -> None:
    """Upgrade schema."""
    
    # 1. Create certifications table if absent
    if not table_exists('certifications'):
        op.create_table('certifications',
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
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
    create_index_if_absent('ix_certifications_expiry_date', 'certifications', ['expiry_date'], unique=False)
    create_index_if_absent('ix_certifications_id', 'certifications', ['id'], unique=False)
    create_index_if_absent('ix_certifications_vendor_id', 'certifications', ['vendor_id'], unique=False)

    # 2. Create compliance_records table if absent
    if not table_exists('compliance_records'):
        op.create_table('compliance_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vendor_id', sa.Integer(), nullable=False),
        sa.Column('compliance_type', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('verification_date', sa.DateTime(), nullable=True),
        sa.Column('verified_by', sa.Integer(), nullable=True),
        sa.Column('remarks', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ),
        sa.ForeignKeyConstraint(['verified_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
    create_index_if_absent('ix_compliance_records_id', 'compliance_records', ['id'], unique=False)
    create_index_if_absent('ix_compliance_records_status', 'compliance_records', ['status'], unique=False)
    create_index_if_absent('ix_compliance_records_vendor_id', 'compliance_records', ['vendor_id'], unique=False)

    # 3. Create contract_renewals table if absent
    if not table_exists('contract_renewals'):
        op.create_table('contract_renewals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('contract_id', sa.Integer(), nullable=False),
        sa.Column('renewal_date', sa.DateTime(), nullable=True),
        sa.Column('new_end_date', sa.DateTime(), nullable=False),
        sa.Column('renewal_value', sa.Float(), nullable=True),
        sa.Column('remarks', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['contract_id'], ['contracts.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
    create_index_if_absent('ix_contract_renewals_contract_id', 'contract_renewals', ['contract_id'], unique=False)
    create_index_if_absent('ix_contract_renewals_id', 'contract_renewals', ['id'], unique=False)

    # 4. Alter contracts columns safely
    if not column_exists('contracts', 'contract_number'):
        op.add_column('contracts', sa.Column('contract_number', sa.String(length=100), nullable=True))
        op.execute("UPDATE contracts SET contract_number = 'CON-' || id WHERE contract_number IS NULL")
        op.alter_column('contracts', 'contract_number', nullable=False)
        
    add_column_if_absent('contracts', sa.Column('procurement_category', sa.String(length=100), nullable=True))
    add_column_if_absent('contracts', sa.Column('payment_terms', sa.String(length=255), nullable=True))
    add_column_if_absent('contracts', sa.Column('sla', sa.String(length=500), nullable=True))
    add_column_if_absent('contracts', sa.Column('warranty_details', sa.String(length=500), nullable=True))
    add_column_if_absent('contracts', sa.Column('responsible_manager', sa.String(length=255), nullable=True))
    add_column_if_absent('contracts', sa.Column('document_url', sa.String(length=500), nullable=True))

    create_index_if_absent('ix_contracts_contract_number', 'contracts', ['contract_number'], unique=True)
    create_index_if_absent('ix_invoices_invoice_number', 'invoices', ['invoice_number'], unique=True)

    # 5. Alter procurement_requests columns to NOT NULL safely
    if column_exists('procurement_requests', 'title'):
        if column_has_nulls('procurement_requests', 'title'):
            op.execute("UPDATE procurement_requests SET title = COALESCE(title, item_description, 'Procurement Request') WHERE title IS NULL")
        op.alter_column('procurement_requests', 'title', existing_type=sa.VARCHAR(length=255), nullable=False)

    if column_exists('procurement_requests', 'product_name'):
        if column_has_nulls('procurement_requests', 'product_name'):
            op.execute("UPDATE procurement_requests SET product_name = COALESCE(product_name, item_description, 'Unknown Product') WHERE product_name IS NULL")
        op.alter_column('procurement_requests', 'product_name', existing_type=sa.VARCHAR(length=255), nullable=False)

    if column_exists('procurement_requests', 'product_category'):
        if column_has_nulls('procurement_requests', 'product_category'):
            op.execute("UPDATE procurement_requests SET product_category = COALESCE(product_category, 'Uncategorized') WHERE product_category IS NULL")
        op.alter_column('procurement_requests', 'product_category', existing_type=sa.VARCHAR(length=100), nullable=False)

    if column_exists('procurement_requests', 'estimated_budget'):
        if column_has_nulls('procurement_requests', 'estimated_budget'):
            op.execute("UPDATE procurement_requests SET estimated_budget = COALESCE(estimated_budget, 0.0) WHERE estimated_budget IS NULL")
        op.alter_column('procurement_requests', 'estimated_budget', existing_type=sa.DOUBLE_PRECISION(precision=53), nullable=False)

    if column_exists('procurement_requests', 'required_delivery_date'):
        if column_has_nulls('procurement_requests', 'required_delivery_date'):
            op.execute("UPDATE procurement_requests SET required_delivery_date = COALESCE(required_delivery_date, request_date, NOW()) WHERE required_delivery_date IS NULL")
        op.alter_column('procurement_requests', 'required_delivery_date', existing_type=postgresql.TIMESTAMP(), nullable=False)

    if column_exists('procurement_requests', 'priority'):
        if column_has_nulls('procurement_requests', 'priority'):
            op.execute("UPDATE procurement_requests SET priority = COALESCE(priority, 'Medium') WHERE priority IS NULL")
        op.alter_column('procurement_requests', 'priority', existing_type=sa.VARCHAR(length=50), nullable=False)

    if column_exists('procurement_requests', 'business_justification'):
        if column_has_nulls('procurement_requests', 'business_justification'):
            op.execute("UPDATE procurement_requests SET business_justification = COALESCE(business_justification, 'N/A') WHERE business_justification IS NULL")
        op.alter_column('procurement_requests', 'business_justification', existing_type=sa.VARCHAR(length=1000), nullable=False)

    # Constraints / indexes on procurement_requests
    drop_constraint_if_present('procurement_requests_request_number_key', 'procurement_requests', constraint_type='unique')
    
    create_index_if_absent('ix_procurement_requests_approved_by', 'procurement_requests', ['approved_by'], unique=False)
    create_index_if_absent('ix_procurement_requests_priority', 'procurement_requests', ['priority'], unique=False)
    create_index_if_absent('ix_procurement_requests_request_number', 'procurement_requests', ['request_number'], unique=True)
    create_index_if_absent('ix_procurement_requests_requested_by', 'procurement_requests', ['requested_by'], unique=False)
    create_index_if_absent('ix_procurement_requests_vendor_id', 'procurement_requests', ['vendor_id'], unique=False)
    
    add_column_if_absent('procurement_requests', sa.Column('vendor_id', sa.Integer(), nullable=True))
    create_fk_if_absent(None, 'procurement_requests', 'vendors', ['vendor_id'], ['id'])

    # 6. Alter purchase_orders safely
    add_column_if_absent('purchase_orders', sa.Column('tax_details', sa.Float(), nullable=True))
    add_column_if_absent('purchase_orders', sa.Column('shipping_address', sa.String(length=500), nullable=True))
    add_column_if_absent('purchase_orders', sa.Column('created_by', sa.Integer(), nullable=True))
    add_column_if_absent('purchase_orders', sa.Column('approved_by', sa.Integer(), nullable=True))
    add_column_if_absent('purchase_orders', sa.Column('po_date', sa.DateTime(), nullable=True))

    drop_constraint_if_present('purchase_orders_po_number_key', 'purchase_orders', constraint_type='unique')
    drop_constraint_if_present('purchase_orders_procurement_request_id_key', 'purchase_orders', constraint_type='unique')

    create_index_if_absent('ix_purchase_orders_approved_by', 'purchase_orders', ['approved_by'], unique=False)
    create_index_if_absent('ix_purchase_orders_created_by', 'purchase_orders', ['created_by'], unique=False)
    create_index_if_absent('ix_purchase_orders_po_number', 'purchase_orders', ['po_number'], unique=True)
    create_index_if_absent('ix_purchase_orders_procurement_request_id', 'purchase_orders', ['procurement_request_id'], unique=True)

    create_fk_if_absent(None, 'purchase_orders', 'users', ['created_by'], ['id'])
    create_fk_if_absent(None, 'purchase_orders', 'users', ['approved_by'], ['id'])

    # 7. Alter users safely
    add_column_if_absent('users', sa.Column('mobile_number', sa.String(length=20), nullable=True))
    add_column_if_absent('users', sa.Column('employee_id', sa.String(length=50), nullable=True))
    add_column_if_absent('users', sa.Column('company_name', sa.String(length=255), nullable=True))
    add_column_if_absent('users', sa.Column('profile_picture_url', sa.String(length=500), nullable=True))

    # 8. Alter vendor_approval_history safely
    add_column_if_absent('vendor_approval_history', sa.Column('action_date', sa.DateTime(), nullable=True))
    create_index_if_absent('ix_vendor_approval_history_acted_by', 'vendor_approval_history', ['acted_by'], unique=False)
    create_index_if_absent('ix_vendor_approval_history_action_date', 'vendor_approval_history', ['action_date'], unique=False)
    drop_column_if_present('vendor_approval_history', 'acted_at')

    # 9. Alter vendors indexes safely
    create_index_if_absent('ix_vendors_approval_status', 'vendors', ['approval_status'], unique=False)
    create_index_if_absent('ix_vendors_gst_number', 'vendors', ['gst_number'], unique=True)
    create_index_if_absent('ix_vendors_pan_number', 'vendors', ['pan_number'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    drop_index_if_present('ix_vendors_pan_number', 'vendors')
    drop_index_if_present('ix_vendors_gst_number', 'vendors')
    drop_index_if_present('ix_vendors_approval_status', 'vendors')

    add_column_if_absent('vendor_approval_history', sa.Column('acted_at', sa.DateTime(), nullable=True))
    drop_index_if_present('ix_vendor_approval_history_action_date', 'vendor_approval_history')
    drop_index_if_present('ix_vendor_approval_history_acted_by', 'vendor_approval_history')
    drop_column_if_present('vendor_approval_history', 'action_date')

    drop_column_if_present('users', 'profile_picture_url')
    drop_column_if_present('users', 'company_name')
    drop_column_if_present('users', 'employee_id')
    drop_column_if_present('users', 'mobile_number')

    drop_fk_if_present('purchase_orders', 'users', ['created_by'], ['id'])
    drop_fk_if_present('purchase_orders', 'users', ['approved_by'], ['id'])

    drop_index_if_present('ix_purchase_orders_procurement_request_id', 'purchase_orders')
    drop_index_if_present('ix_purchase_orders_po_number', 'purchase_orders')
    drop_index_if_present('ix_purchase_orders_created_by', 'purchase_orders')
    drop_index_if_present('ix_purchase_orders_approved_by', 'purchase_orders')

    if not constraint_exists('purchase_orders', 'purchase_orders_procurement_request_id_key', 'unique'):
        op.create_unique_constraint('purchase_orders_procurement_request_id_key', 'purchase_orders', ['procurement_request_id'])
    if not constraint_exists('purchase_orders', 'purchase_orders_po_number_key', 'unique'):
        op.create_unique_constraint('purchase_orders_po_number_key', 'purchase_orders', ['po_number'])

    drop_column_if_present('purchase_orders', 'po_date')
    drop_column_if_present('purchase_orders', 'approved_by')
    drop_column_if_present('purchase_orders', 'created_by')
    drop_column_if_present('purchase_orders', 'shipping_address')
    drop_column_if_present('purchase_orders', 'tax_details')

    drop_fk_if_present('procurement_requests', 'vendors', ['vendor_id'], ['id'])

    drop_index_if_present('ix_procurement_requests_vendor_id', 'procurement_requests')
    drop_index_if_present('ix_procurement_requests_requested_by', 'procurement_requests')
    drop_index_if_present('ix_procurement_requests_request_number', 'procurement_requests')
    drop_index_if_present('ix_procurement_requests_priority', 'procurement_requests')
    drop_index_if_present('ix_procurement_requests_approved_by', 'procurement_requests')

    if not constraint_exists('procurement_requests', 'procurement_requests_request_number_key', 'unique'):
        op.create_unique_constraint('procurement_requests_request_number_key', 'procurement_requests', ['request_number'])

    if column_exists('procurement_requests', 'business_justification'):
        op.alter_column('procurement_requests', 'business_justification', existing_type=sa.VARCHAR(length=1000), nullable=True)
    if column_exists('procurement_requests', 'priority'):
        op.alter_column('procurement_requests', 'priority', existing_type=sa.VARCHAR(length=50), nullable=True)
    if column_exists('procurement_requests', 'required_delivery_date'):
        op.alter_column('procurement_requests', 'required_delivery_date', existing_type=postgresql.TIMESTAMP(), nullable=True)
    if column_exists('procurement_requests', 'estimated_budget'):
        op.alter_column('procurement_requests', 'estimated_budget', existing_type=sa.DOUBLE_PRECISION(precision=53), nullable=True)
    if column_exists('procurement_requests', 'product_category'):
        op.alter_column('procurement_requests', 'product_category', existing_type=sa.VARCHAR(length=100), nullable=True)
    if column_exists('procurement_requests', 'product_name'):
        op.alter_column('procurement_requests', 'product_name', existing_type=sa.VARCHAR(length=255), nullable=True)
    if column_exists('procurement_requests', 'title'):
        op.alter_column('procurement_requests', 'title', existing_type=sa.VARCHAR(length=255), nullable=True)

    drop_column_if_present('procurement_requests', 'vendor_id')

    drop_index_if_present('ix_invoices_invoice_number', 'invoices')
    drop_index_if_present('ix_contracts_contract_number', 'contracts')

    drop_column_if_present('contracts', 'document_url')
    drop_column_if_present('contracts', 'responsible_manager')
    drop_column_if_present('contracts', 'warranty_details')
    drop_column_if_present('contracts', 'sla')
    drop_column_if_present('contracts', 'payment_terms')
    drop_column_if_present('contracts', 'procurement_category')
    drop_column_if_present('contracts', 'contract_number')

    # Drop contract renewals
    drop_index_if_present('ix_contract_renewals_id', 'contract_renewals')
    drop_index_if_present('ix_contract_renewals_contract_id', 'contract_renewals')
    if table_exists('contract_renewals'):
        op.drop_table('contract_renewals')

    # Drop compliance records
    drop_index_if_present('ix_compliance_records_vendor_id', 'compliance_records')
    drop_index_if_present('ix_compliance_records_status', 'compliance_records')
    drop_index_if_present('ix_compliance_records_id', 'compliance_records')
    if table_exists('compliance_records'):
        op.drop_table('compliance_records')

    # Drop certifications
    drop_index_if_present('ix_certifications_vendor_id', 'certifications')
    drop_index_if_present('ix_certifications_id', 'certifications')
    drop_index_if_present('ix_certifications_expiry_date', 'certifications')
    if table_exists('certifications'):
        op.drop_table('certifications')
