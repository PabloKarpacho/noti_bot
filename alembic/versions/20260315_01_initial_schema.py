"""Initial schema

Revision ID: 20260315_01
Revises:
Create Date: 2026-03-15 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260315_01"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("user_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_tg_id", sa.String(length=36), nullable=False),
        sa.Column("timezone", sa.String(length=50), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("user_id"),
    )
    op.create_index("ix_users_user_id", "users", ["user_id"], unique=False)
    op.create_index("ix_users_user_tg_id", "users", ["user_tg_id"], unique=True)
    op.create_index("ix_users_created_at", "users", ["created_at"], unique=False)

    op.create_table(
        "notification_templates",
        sa.Column(
            "notification_template_id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("message", sa.String(length=500), nullable=False),
        sa.Column("time_start", sa.Time(timezone=False), nullable=False),
        sa.Column("sending_interval_minutes", sa.Integer(), nullable=False),
        sa.Column("time_stop", sa.Time(timezone=False), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("notification_template_id"),
    )
    op.create_index(
        "ix_notification_templates_notification_template_id",
        "notification_templates",
        ["notification_template_id"],
        unique=False,
    )
    op.create_index(
        "ix_notification_templates_user_id",
        "notification_templates",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_notification_templates_created_at",
        "notification_templates",
        ["created_at"],
        unique=False,
    )

    op.create_table(
        "notifications",
        sa.Column("notification_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("template_id", sa.Integer(), nullable=False),
        sa.Column("marked_as_done", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["template_id"],
            ["notification_templates.notification_template_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("notification_id"),
    )
    op.create_index(
        "ix_notifications_notification_id",
        "notifications",
        ["notification_id"],
        unique=False,
    )
    op.create_index(
        "ix_notifications_template_id",
        "notifications",
        ["template_id"],
        unique=False,
    )
    op.create_index(
        "ix_notifications_created_at",
        "notifications",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_notifications_created_at", table_name="notifications")
    op.drop_index("ix_notifications_template_id", table_name="notifications")
    op.drop_index("ix_notifications_notification_id", table_name="notifications")
    op.drop_table("notifications")

    op.drop_index(
        "ix_notification_templates_created_at", table_name="notification_templates"
    )
    op.drop_index(
        "ix_notification_templates_user_id", table_name="notification_templates"
    )
    op.drop_index(
        "ix_notification_templates_notification_template_id",
        table_name="notification_templates",
    )
    op.drop_table("notification_templates")

    op.drop_index("ix_users_created_at", table_name="users")
    op.drop_index("ix_users_user_tg_id", table_name="users")
    op.drop_index("ix_users_user_id", table_name="users")
    op.drop_table("users")
