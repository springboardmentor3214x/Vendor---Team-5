"""merge migration heads 34d03b0bca5d and 7a8f9b0c1d2e

Revision ID: 9f8e7d6c5b4a
Revises: 34d03b0bca5d, 7a8f9b0c1d2e
Create Date: 2026-07-29 20:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f8e7d6c5b4a'
down_revision: Union[str, Sequence[str], None] = ('34d03b0bca5d', '7a8f9b0c1d2e')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
