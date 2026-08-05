"""add Module 7 communication discussion files and activity log updates

Revision ID: e7f8a9b0c1d2
Revises: a1b2c3d4e5f6
Create Date: 2026-08-04 20:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = 'e7f8a9b0c1d2'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)
    tables = inspector.get_table_names()

    # 1. discussions table
    if 'discussions' not in tables:
        op.create_table(
            'discussions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(length=255), nullable=False),
            sa.Column('created_by_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('vendor_id', sa.Integer(), sa.ForeignKey('vendors.id'), nullable=True),
            sa.Column('procurement_request_id', sa.Integer(), sa.ForeignKey('procurement_requests.id'), nullable=True),
            sa.Column('purchase_order_id', sa.Integer(), sa.ForeignKey('purchase_orders.id'), nullable=True),
            sa.Column('contract_id', sa.Integer(), sa.ForeignKey('contracts.id'), nullable=True),
            sa.Column('invoice_id', sa.Integer(), sa.ForeignKey('invoices.id'), nullable=True),
            sa.Column('status', sa.String(length=50), nullable=True, server_default='OPEN'),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_discussions_id', 'discussions', ['id'], unique=False)
        op.create_index('ix_discussions_title', 'discussions', ['title'], unique=False)
        op.create_index('ix_discussions_created_by_id', 'discussions', ['created_by_id'], unique=False)

    # 2. discussion_participants table
    if 'discussion_participants' not in tables:
        op.create_table(
            'discussion_participants',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('discussion_id', sa.Integer(), sa.ForeignKey('discussions.id'), nullable=False),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('joined_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_discussion_participants_id', 'discussion_participants', ['id'], unique=False)
        op.create_index('ix_discussion_participants_discussion_id', 'discussion_participants', ['discussion_id'], unique=False)

    # 3. communication_files table
    if 'communication_files' not in tables:
        op.create_table(
            'communication_files',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('filename', sa.String(length=255), nullable=False),
            sa.Column('file_path', sa.String(length=500), nullable=False),
            sa.Column('file_type', sa.String(length=100), nullable=True),
            sa.Column('file_size', sa.Integer(), nullable=True),
            sa.Column('uploaded_by_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('message_id', sa.Integer(), sa.ForeignKey('communications.id'), nullable=True),
            sa.Column('discussion_id', sa.Integer(), sa.ForeignKey('discussions.id'), nullable=True),
            sa.Column('vendor_id', sa.Integer(), sa.ForeignKey('vendors.id'), nullable=True),
            sa.Column('procurement_request_id', sa.Integer(), sa.ForeignKey('procurement_requests.id'), nullable=True),
            sa.Column('purchase_order_id', sa.Integer(), sa.ForeignKey('purchase_orders.id'), nullable=True),
            sa.Column('contract_id', sa.Integer(), sa.ForeignKey('contracts.id'), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_communication_files_id', 'communication_files', ['id'], unique=False)

    # 4. communications table column updates
    if 'communications' in tables:
        comm_cols = [c['name'] for c in inspector.get_columns('communications')]
        if 'receiver_id' not in comm_cols:
            op.add_column('communications', sa.Column('receiver_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True))
        if 'purchase_order_id' not in comm_cols:
            op.add_column('communications', sa.Column('purchase_order_id', sa.Integer(), sa.ForeignKey('purchase_orders.id'), nullable=True))
        if 'contract_id' not in comm_cols:
            op.add_column('communications', sa.Column('contract_id', sa.Integer(), sa.ForeignKey('contracts.id'), nullable=True))
        if 'invoice_id' not in comm_cols:
            op.add_column('communications', sa.Column('invoice_id', sa.Integer(), sa.ForeignKey('invoices.id'), nullable=True))
        if 'discussion_id' not in comm_cols:
            op.add_column('communications', sa.Column('discussion_id', sa.Integer(), sa.ForeignKey('discussions.id'), nullable=True))
        if 'message_type' not in comm_cols:
            op.add_column('communications', sa.Column('message_type', sa.String(length=50), nullable=True, server_default='DIRECT'))
        if 'is_read' not in comm_cols:
            op.add_column('communications', sa.Column('is_read', sa.Boolean(), nullable=True, server_default='0'))
        if 'read_at' not in comm_cols:
            op.add_column('communications', sa.Column('read_at', sa.DateTime(), nullable=True))

    # 5. activity_logs table column updates
    if 'activity_logs' in tables:
        act_cols = [c['name'] for c in inspector.get_columns('activity_logs')]
        if 'related_entity_type' not in act_cols:
            op.add_column('activity_logs', sa.Column('related_entity_type', sa.String(length=100), nullable=True))
        if 'related_entity_id' not in act_cols:
            op.add_column('activity_logs', sa.Column('related_entity_id', sa.Integer(), nullable=True))
        if 'ip_address' not in act_cols:
            op.add_column('activity_logs', sa.Column('ip_address', sa.String(length=45), nullable=True))


def downgrade():
    pass
