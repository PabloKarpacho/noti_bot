"""Add sticker and last bot message columns

Revision ID: 20260315_02
Revises: 20260315_01
Create Date: 2026-03-15 00:00:01.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260315_02"
down_revision: Union[str, None] = "20260315_01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "notifications",
        sa.Column("sticker_sent", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "notifications",
        sa.Column("last_bot_message_id", sa.Integer(), nullable=True),
    )
    op.alter_column("notifications", "sticker_sent", server_default=None)


def downgrade() -> None:
    op.drop_column("notifications", "last_bot_message_id")
    op.drop_column("notifications", "sticker_sent")
