"""add missing contract_id and compliance_status to compliance_records

Revision ID: a1b2c3d4e5f6
Revises: 9f8e7d6c5b4a
Create Date: 2026-07-29 22:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '9f8e7d6c5b4a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def get_fresh_inspector():
    conn = op.get_bind()
    return sa.inspect(conn)


def upgrade() -> None:
    inspector = get_fresh_inspector()

    if inspector.has_table('compliance_records'):
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

    if inspector.has_table('procurement_recommendations'):
        pr_cols = [c['name'] for c in inspector.get_columns('procurement_recommendations')]
        pr_indexes = [idx['name'] for idx in inspector.get_indexes('procurement_recommendations')]

        with op.batch_alter_table('procurement_recommendations') as batch_op:
            if 'category_id' not in pr_cols:
                batch_op.add_column(sa.Column('category_id', sa.Integer(), nullable=True))
                batch_op.create_foreign_key('fk_procurement_recommendations_category_id', 'vendor_categories', ['category_id'], ['id'])
                if 'ix_procurement_recommendations_category_id' not in pr_indexes:
                    batch_op.create_index('ix_procurement_recommendations_category_id', ['category_id'], unique=False)
            if 'recommendation_score' not in pr_cols:
                batch_op.add_column(sa.Column('recommendation_score', sa.Float(), nullable=True))
            if 'generated_at' not in pr_cols:
                batch_op.add_column(sa.Column('generated_at', sa.DateTime(), nullable=True))
                if 'ix_procurement_recommendations_generated_at' not in pr_indexes:
                    batch_op.create_index('ix_procurement_recommendations_generated_at', ['generated_at'], unique=False)


def downgrade() -> None:
    pass
