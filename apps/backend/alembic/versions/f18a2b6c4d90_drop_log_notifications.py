"""drop log notifications, consolidate read-state onto user_notifications

Revision ID: f18a2b6c4d90
Revises: e040c3f7a072
Create Date: 2026-07-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'f18a2b6c4d90'
down_revision: Union[str, Sequence[str], None] = 'e040c3f7a072'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("DROP INDEX IF EXISTS log.idx_notifications_unread")
    op.execute("DROP INDEX IF EXISTS log.idx_notifications_recipient_created")
    op.execute("DROP TABLE IF EXISTS log.notifications")

    op.add_column('notifications', sa.Column('payload', postgresql.JSONB(), nullable=True), schema='reference')
    op.drop_column('notifications', 'is_read', schema='reference')
    op.drop_column('user_notifications', 'is_read', schema='reference')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('user_notifications', sa.Column('is_read', sa.Boolean(), server_default=sa.text('false'), nullable=False), schema='reference')
    op.add_column('notifications', sa.Column('is_read', sa.Boolean(), server_default=sa.text('false'), nullable=False), schema='reference')
    op.drop_column('notifications', 'payload', schema='reference')

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
