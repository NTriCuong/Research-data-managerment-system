"""add notifications

Revision ID: 9d2a4f6b8c31
Revises: 6b7f9c2d4e10
Create Date: 2026-06-24 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "9d2a4f6b8c31"
down_revision: Union[str, Sequence[str], None] = "6b7f9c2d4e10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS log.notifications (
            notification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            recipient_user_id UUID NOT NULL REFERENCES auth.users(user_id),
            actor_user_id UUID REFERENCES auth.users(user_id),
            event_type VARCHAR(100) NOT NULL,
            title VARCHAR(255) NOT NULL,
            message TEXT NOT NULL,
            target_url TEXT,
            payload JSONB,
            read_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_notifications_recipient_created ON log.notifications(recipient_user_id, created_at DESC)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_notifications_unread ON log.notifications(recipient_user_id) WHERE read_at IS NULL")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS log.notifications")
