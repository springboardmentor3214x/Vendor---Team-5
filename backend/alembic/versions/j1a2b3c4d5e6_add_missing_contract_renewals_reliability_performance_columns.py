"""add missing contract_renewals, reliability, and performance columns for parity

Revision ID: j1a2b3c4d5e6
Revises: i0a1b2c3d4e5
Create Date: 2026-08-13 19:48:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision: str = 'j1a2b3c4d5e6'
down_revision: Union[str, Sequence[str], None] = 'i0a1b2c3d4e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)

    # 1. contract_renewals: add missing columns previous_end_date, renewed_by, renewal_notes, revised_contract_value
    if inspector.has_table('contract_renewals'):
        cr_cols = [c['name'] for c in inspector.get_columns('contract_renewals')]
        cr_indexes = [idx['name'] for idx in inspector.get_indexes('contract_renewals')]
        cr_fks = [fk['name'] for fk in inspector.get_foreign_keys('contract_renewals')]

        with op.batch_alter_table('contract_renewals') as batch_op:
            if 'previous_end_date' not in cr_cols:
                batch_op.add_column(sa.Column('previous_end_date', sa.DateTime(), nullable=True))

            if 'renewed_by' not in cr_cols:
                batch_op.add_column(sa.Column('renewed_by', sa.Integer(), nullable=True))
                if inspector.has_table('users') and 'fk_contract_renewals_renewed_by_users' not in cr_fks:
                    batch_op.create_foreign_key(
                        'fk_contract_renewals_renewed_by_users',
                        'users',
                        ['renewed_by'],
                        ['id']
                    )
                if 'ix_contract_renewals_renewed_by' not in cr_indexes:
                    batch_op.create_index(
                        'ix_contract_renewals_renewed_by',
                        ['renewed_by'],
                        unique=False
                    )

            if 'renewal_notes' not in cr_cols:
                batch_op.add_column(sa.Column('renewal_notes', sa.Text(), nullable=True))

            if 'revised_contract_value' not in cr_cols:
                batch_op.add_column(sa.Column('revised_contract_value', sa.Float(), nullable=True))
    else:
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
            sa.Column('renewal_value', sa.Float(), nullable=True, server_default='0.0'),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['contract_id'], ['contracts.id']),
            sa.ForeignKeyConstraint(['renewed_by'], ['users.id'], name='fk_contract_renewals_renewed_by_users'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_contract_renewals_contract_id'), 'contract_renewals', ['contract_id'], unique=False)
        op.create_index(op.f('ix_contract_renewals_id'), 'contract_renewals', ['id'], unique=False)
        op.create_index(op.f('ix_contract_renewals_renewed_by'), 'contract_renewals', ['renewed_by'], unique=False)

    # 2. vendor_reliability & performance_trends: add procurement_history_score if absent and backfill
    if inspector.has_table('vendor_reliability'):
        vr_cols = [c['name'] for c in inspector.get_columns('vendor_reliability')]
        with op.batch_alter_table('vendor_reliability') as batch_op:
            if 'procurement_history_score' not in vr_cols:
                batch_op.add_column(sa.Column('procurement_history_score', sa.Float(), nullable=True, server_default='0.0'))
        op.execute("UPDATE vendor_reliability SET procurement_history_score = 0.0 WHERE procurement_history_score IS NULL")

    if inspector.has_table('performance_trends'):
        pt_cols = [c['name'] for c in inspector.get_columns('performance_trends')]
        with op.batch_alter_table('performance_trends') as batch_op:
            if 'procurement_history_score' not in pt_cols:
                batch_op.add_column(sa.Column('procurement_history_score', sa.Float(), nullable=True, server_default='0.0'))
        op.execute("UPDATE performance_trends SET procurement_history_score = 0.0 WHERE procurement_history_score IS NULL")

    # 3. performance_records: add average_communication_score if absent and backfill
    if inspector.has_table('performance_records'):
        pr_cols = [c['name'] for c in inspector.get_columns('performance_records')]
        with op.batch_alter_table('performance_records') as batch_op:
            if 'average_communication_score' not in pr_cols:
                batch_op.add_column(sa.Column('average_communication_score', sa.Float(), nullable=True, server_default='0.0'))
        op.execute("UPDATE performance_records SET average_communication_score = 0.0 WHERE average_communication_score IS NULL")


def downgrade() -> None:
    pass
