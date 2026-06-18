"""consolidate core search FTS

Revision ID: 6b7f9c2d4e10
Revises: 3f4d2c1b9a70
Create Date: 2026-06-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "6b7f9c2d4e10"
down_revision: Union[str, Sequence[str], None] = "3f4d2c1b9a70"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove duplicate FTS objects and rebuild with the original app function."""
    for table_name in ("research_object_authors", "research_object_keywords", "research_object_domains"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_core_{table_name}_search_vector ON core.{table_name}")
    op.execute("DROP TRIGGER IF EXISTS trg_reference_research_domains_core_search_vector ON reference.research_domains")
    op.execute("DROP TRIGGER IF EXISTS trg_reference_keywords_core_search_vector ON reference.keywords")
    op.execute("DROP TRIGGER IF EXISTS trg_core_research_objects_search_vector ON core.research_objects")
    op.execute("DROP FUNCTION IF EXISTS core.refresh_research_object_search_vector_from_domain()")
    op.execute("DROP FUNCTION IF EXISTS core.refresh_research_object_search_vector_from_keyword()")
    op.execute("DROP FUNCTION IF EXISTS core.refresh_research_object_search_vector_from_relation()")
    op.execute("DROP FUNCTION IF EXISTS core.refresh_research_object_search_vector()")
    op.execute("DROP FUNCTION IF EXISTS core.rebuild_research_object_search_vector(uuid)")
    op.execute("DROP INDEX IF EXISTS core.ix_core_research_objects_search_vector")
    op.execute("SELECT app.refresh_core_search_vector(research_id) FROM core.research_objects")


def downgrade() -> None:
    """The retained app-level FTS implementation remains valid."""
