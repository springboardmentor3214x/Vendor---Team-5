"""merge_heads

Revision ID: 5694ad64a9c0
Revises: 15ba89028e5b, 605aec7d0e6b
Create Date: 2026-07-28 18:58:45.329362

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5694ad64a9c0'
down_revision: Union[str, Sequence[str], None] = ('15ba89028e5b', '605aec7d0e6b')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
