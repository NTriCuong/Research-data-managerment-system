"""add view and download counts to public research objects

Revision ID: a7c9e1f3b520
Revises: 2f0fbd1fe4dd
Create Date: 2026-07-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a7c9e1f3b520"
down_revision: Union[str, Sequence[str], None] = "2f0fbd1fe4dd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "research_objects",
        sa.Column(
            "view_count",
            sa.BigInteger(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        schema="core",
    )
    op.add_column(
        "research_objects",
        sa.Column(
            "download_count",
            sa.BigInteger(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        schema="core",
    )

    # Preserve views already recorded before the counter columns were added.
    op.execute(
        """
        UPDATE core.research_objects AS research
        SET view_count = view_totals.total
        FROM (
            SELECT research_id, COUNT(*)::BIGINT AS total
            FROM log.research_object_view
            GROUP BY research_id
        ) AS view_totals
        WHERE research.research_id = view_totals.research_id
          AND research.access_level = 'public'
        """
    )

    op.create_check_constraint(
        "ck_core_research_objects_view_count_nonnegative",
        "research_objects",
        "view_count >= 0",
        schema="core",
    )
    op.create_check_constraint(
        "ck_core_research_objects_download_count_nonnegative",
        "research_objects",
        "download_count >= 0",
        schema="core",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_core_research_objects_download_count_nonnegative",
        "research_objects",
        schema="core",
        type_="check",
    )
    op.drop_constraint(
        "ck_core_research_objects_view_count_nonnegative",
        "research_objects",
        schema="core",
        type_="check",
    )
    op.drop_column("research_objects", "download_count", schema="core")
    op.drop_column("research_objects", "view_count", schema="core")
