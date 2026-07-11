"""them table views vao logs

Revision ID: 2f0fbd1fe4dd
Revises: f18a2b6c4d90
Create Date: 2026-07-10 23:43:06.579058

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '2f0fbd1fe4dd'
down_revision: Union[str, Sequence[str], None] = 'f18a2b6c4d90'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'research_object_view',
        sa.Column(
            'view_id',
            postgresql.UUID(as_uuid=True),
            server_default=sa.text('gen_random_uuid()'),
            nullable=False,
        ),
        sa.Column(
            'research_id',
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            'viewed_at',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column(
            'viewed_date',
            sa.Date(),
            sa.Computed(
                "(viewed_at AT TIME ZONE 'Asia/Ho_Chi_Minh')::DATE",
                persisted=True,
            ),
            nullable=False,
        ),
        sa.Column(
            'viewed_year',
            sa.Integer(),
            sa.Computed(
                "EXTRACT(YEAR FROM viewed_at AT TIME ZONE 'Asia/Ho_Chi_Minh')::INT",
                persisted=True,
            ),
            nullable=False,
        ),
        sa.Column(
            'viewed_month',
            sa.Integer(),
            sa.Computed(
                "EXTRACT(MONTH FROM viewed_at AT TIME ZONE 'Asia/Ho_Chi_Minh')::INT",
                persisted=True,
            ),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ['research_id'],
            ['core.research_objects.research_id'],
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('view_id'),
        schema='log',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('research_object_view', schema='log')
