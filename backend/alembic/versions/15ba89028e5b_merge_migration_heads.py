"""merge migration heads

Revision ID: 15ba89028e5b
Revises: 145083324cb4, 5b3b58ff7347
Create Date: 2026-07-28 05:44:58.745906

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '15ba89028e5b'
down_revision: Union[str, Sequence[str], None] = ('145083324cb4', '5b3b58ff7347')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
