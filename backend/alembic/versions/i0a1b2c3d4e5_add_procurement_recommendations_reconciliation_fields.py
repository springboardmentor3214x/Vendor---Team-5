"""reconcile procurement_recommendations missing columns (category_id, recommendation_score, generated_at)

Revision ID: i0a1b2c3d4e5
Revises: h0a1b2c3d4e5
Create Date: 2026-08-12 20:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision: str = 'i0a1b2c3d4e5'
down_revision: Union[str, Sequence[str], None] = 'h0a1b2c3d4e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)

    if inspector.has_table('procurement_recommendations'):
        existing_cols = [c['name'] for c in inspector.get_columns('procurement_recommendations')]
        existing_indexes = [idx['name'] for idx in inspector.get_indexes('procurement_recommendations')]

        with op.batch_alter_table('procurement_recommendations') as batch_op:
            if 'category_id' not in existing_cols:
                batch_op.add_column(sa.Column('category_id', sa.Integer(), nullable=True))
                if inspector.has_table('vendor_categories'):
                    batch_op.create_foreign_key(
                        'fk_procurement_recommendations_category_id',
                        'vendor_categories',
                        ['category_id'],
                        ['id']
                    )
                if 'ix_procurement_recommendations_category_id' not in existing_indexes:
                    batch_op.create_index(
                        'ix_procurement_recommendations_category_id',
                        ['category_id'],
                        unique=False
                    )

            if 'recommendation_score' not in existing_cols:
                batch_op.add_column(sa.Column('recommendation_score', sa.Float(), nullable=True))

            if 'generated_at' not in existing_cols:
                batch_op.add_column(sa.Column('generated_at', sa.DateTime(), nullable=True, server_default=sa.func.now()))
                if 'ix_procurement_recommendations_generated_at' not in existing_indexes:
                    batch_op.create_index(
                        'ix_procurement_recommendations_generated_at',
                        ['generated_at'],
                        unique=False
                    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)

    if inspector.has_table('procurement_recommendations'):
        existing_cols = [c['name'] for c in inspector.get_columns('procurement_recommendations')]
        existing_indexes = [idx['name'] for idx in inspector.get_indexes('procurement_recommendations')]

        with op.batch_alter_table('procurement_recommendations') as batch_op:
            if 'generated_at' in existing_cols:
                if 'ix_procurement_recommendations_generated_at' in existing_indexes:
                    batch_op.drop_index('ix_procurement_recommendations_generated_at')
                batch_op.drop_column('generated_at')

            if 'recommendation_score' in existing_cols:
                batch_op.drop_column('recommendation_score')

            if 'category_id' in existing_cols:
                if 'ix_procurement_recommendations_category_id' in existing_indexes:
                    batch_op.drop_index('ix_procurement_recommendations_category_id')
                fk_names = [fk['name'] for fk in inspector.get_foreign_keys('procurement_recommendations')]
                if 'fk_procurement_recommendations_category_id' in fk_names:
                    batch_op.drop_constraint('fk_procurement_recommendations_category_id', type_='foreignkey')
                batch_op.drop_column('category_id')
