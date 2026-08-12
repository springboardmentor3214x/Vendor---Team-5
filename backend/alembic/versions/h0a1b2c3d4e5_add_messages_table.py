"""add dedicated messages table with composite indexes

Revision ID: h0a1b2c3d4e5
Revises: b2c3d4e5f6a7, g9b0c1d2e3f4
Create Date: 2026-08-12 11:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = 'h0a1b2c3d4e5'
down_revision = ('b2c3d4e5f6a7', 'g9b0c1d2e3f4')
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)
    tables = inspector.get_table_names()

    if 'messages' not in tables:
        related_entity_type_enum = sa.Enum(
            'vendor', 'procurement_request', 'purchase_order', 'contract', 'none',
            name='related_entity_type'
        )
        op.create_table(
            'messages',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('sender_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('receiver_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('related_entity_type', related_entity_type_enum, nullable=False, server_default='none'),
            sa.Column('related_entity_id', sa.Integer(), nullable=True),
            sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column('read_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_messages_id', 'messages', ['id'], unique=False)
        op.create_index('ix_messages_sender_id_created_at', 'messages', ['sender_id', 'created_at'], unique=False)
        op.create_index('ix_messages_receiver_id_is_read_created_at', 'messages', ['receiver_id', 'is_read', 'created_at'], unique=False)


def downgrade():
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)
    tables = inspector.get_table_names()

    if 'messages' in tables:
        op.drop_index('ix_messages_receiver_id_is_read_created_at', table_name='messages')
        op.drop_index('ix_messages_sender_id_created_at', table_name='messages')
        op.drop_index('ix_messages_id', table_name='messages')
        op.drop_table('messages')
        sa.Enum(name='related_entity_type').drop(bind, checkfirst=True)
