"""add content_type and uploaded_by to vendor_documents

Revision ID: 5b3b58ff7347
Revises: 5e725b13cee9
Create Date: 2026-07-27 20:00:32.776701

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5b3b58ff7347'
down_revision: Union[str, Sequence[str], None] = '5e725b13cee9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()
    inspect_obj = sa.inspect(conn)
    tables = inspect_obj.get_table_names()

    # 1. Handle vendor_approval_history table
    if 'vendor_approval_history' not in tables:
        # Create table from scratch
        op.create_table('vendor_approval_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vendor_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('remarks', sa.String(length=1000), nullable=True),
        sa.Column('acted_by', sa.Integer(), nullable=True),
        sa.Column('acted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['acted_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_vendor_approval_history_id'), 'vendor_approval_history', ['id'], unique=False)
        op.create_index(op.f('ix_vendor_approval_history_vendor_id'), 'vendor_approval_history', ['vendor_id'], unique=False)
    else:
        # Table exists - align columns
        columns = [c['name'] for c in inspect_obj.get_columns('vendor_approval_history')]
        
        # Rename approved_by -> acted_by if present
        if 'approved_by' in columns and 'acted_by' not in columns:
            op.alter_column('vendor_approval_history', 'approved_by', new_column_name='acted_by')
            fkeys = inspect_obj.get_foreign_keys('vendor_approval_history')
            has_acted_by_fk = any('acted_by' in fk['referred_columns'] or 'acted_by' in fk['constrained_columns'] for fk in fkeys)
            if not has_acted_by_fk:
                op.create_foreign_key(
                    'fk_vendor_approval_history_acted_by_users',
                    'vendor_approval_history', 'users',
                    ['acted_by'], ['id']
                )

        # Rename action_date -> acted_at if present
        if 'action_date' in columns and 'acted_at' not in columns:
            op.alter_column('vendor_approval_history', 'action_date', new_column_name='acted_at')

        # Check indexes
        indexes = [idx['name'] for idx in inspect_obj.get_indexes('vendor_approval_history')]
        if 'ix_vendor_approval_history_id' not in indexes:
            op.create_index('ix_vendor_approval_history_id', 'vendor_approval_history', ['id'], unique=False)
        if 'ix_vendor_approval_history_vendor_id' not in indexes:
            op.create_index('ix_vendor_approval_history_vendor_id', 'vendor_approval_history', ['vendor_id'], unique=False)

    # 2. Handle vendor_documents columns
    doc_columns = [c['name'] for c in inspect_obj.get_columns('vendor_documents')]
    if 'content_type' not in doc_columns:
        op.add_column('vendor_documents', sa.Column('content_type', sa.String(length=100), nullable=True))
        
    if 'uploaded_by' not in doc_columns:
        op.add_column('vendor_documents', sa.Column('uploaded_by', sa.Integer(), nullable=True))
        fkeys = inspect_obj.get_foreign_keys('vendor_documents')
        has_uploaded_by_fk = any('uploaded_by' in fk['constrained_columns'] for fk in fkeys)
        if not has_uploaded_by_fk:
            op.create_foreign_key(
                'fk_vendor_documents_uploaded_by_users',
                'vendor_documents', 'users',
                ['uploaded_by'], ['id']
            )


def downgrade() -> None:
    """Downgrade schema."""
    conn = op.get_bind()
    inspect_obj = sa.inspect(conn)
    tables = inspect_obj.get_table_names()

    # Drop columns and constraints from vendor_documents if they exist
    if 'vendor_documents' in tables:
        columns = [c['name'] for c in inspect_obj.get_columns('vendor_documents')]
        fkeys = inspect_obj.get_foreign_keys('vendor_documents')
        
        has_uploaded_by_fk = any('uploaded_by' in fk['constrained_columns'] for fk in fkeys)
        if has_uploaded_by_fk:
            fk_name = next((fk['name'] for fk in fkeys if 'uploaded_by' in fk['constrained_columns']), None)
            if fk_name:
                op.drop_constraint(fk_name, 'vendor_documents', type_='foreignkey')
                
        if 'uploaded_by' in columns:
            op.drop_column('vendor_documents', 'uploaded_by')
        if 'content_type' in columns:
            op.drop_column('vendor_documents', 'content_type')

    # Drop vendor_approval_history table if exists
    if 'vendor_approval_history' in tables:
        op.drop_table('vendor_approval_history')

