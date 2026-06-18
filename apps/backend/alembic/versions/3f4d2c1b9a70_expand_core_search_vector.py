"""expand core search vector

Revision ID: 3f4d2c1b9a70
Revises: 8c689e6ab5e8
Create Date: 2026-06-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "3f4d2c1b9a70"
down_revision: Union[str, Sequence[str], None] = "8c689e6ab5e8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Rebuild vectors with the original app-level FTS implementation."""
    op.execute("SELECT app.refresh_core_search_vector(research_id) FROM core.research_objects")


def downgrade() -> None:
    """The previous revision already contains the retained FTS implementation."""
