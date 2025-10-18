"""empty message

Revision ID: 64e2273dd621
Revises: 0c1406fbafcb
Create Date: 2025-10-18 13:35:01.950020

"""

from typing import Optional, Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "64e2273dd621"
down_revision: Optional[str] = "0c1406fbafcb"
branch_labels: Optional[Sequence[str]] = None
depends_on: Optional[Sequence[str]] = None


def upgrade() -> None:
    op.add_column(
        "admin", sa.Column("is_superadmin", sa.Boolean(), server_default="false", nullable=False),
        schema="users",
    )


def downgrade() -> None:
    op.drop_column("admin", "is_superadmin", schema="users")
