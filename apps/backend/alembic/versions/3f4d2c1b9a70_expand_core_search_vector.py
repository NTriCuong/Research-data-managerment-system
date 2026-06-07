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
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent")
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_core_research_objects_search_vector
        ON core.research_objects
        USING GIN (search_vector)
        """
    )
    op.execute(
        """
        CREATE OR REPLACE FUNCTION core.rebuild_research_object_search_vector(target_research_id uuid)
        RETURNS void
        LANGUAGE plpgsql
        AS $$
        BEGIN
            UPDATE core.research_objects AS ro
            SET search_vector =
                setweight(to_tsvector('simple', unaccent(coalesce(ro.title, ''))), 'A') ||
                setweight(to_tsvector('simple', unaccent(coalesce(ro.identifier, ''))), 'A') ||
                setweight(to_tsvector('simple', unaccent(coalesce(ro.abstract, ''))), 'B') ||
                setweight(to_tsvector('simple', unaccent(coalesce((
                    SELECT string_agg(
                        concat_ws(' ', a.full_name, a.email, a.affiliation),
                        ' '
                        ORDER BY a.author_order
                    )
                    FROM core.research_object_authors AS a
                    WHERE a.research_id = ro.research_id
                ), ''))), 'B') ||
                setweight(to_tsvector('simple', unaccent(coalesce((
                    SELECT string_agg(concat_ws(' ', k.keyword_text, k.normalized_text), ' ' ORDER BY k.keyword_text)
                    FROM core.research_object_keywords AS rok
                    JOIN reference.keywords AS k ON k.keyword_id = rok.keyword_id
                    WHERE rok.research_id = ro.research_id
                ), ''))), 'B') ||
                setweight(to_tsvector('simple', unaccent(coalesce((
                    SELECT string_agg(
                        concat_ws(' ', d.domain_code, d.domain_name, d.description),
                        ' '
                        ORDER BY d.domain_name
                    )
                    FROM core.research_object_domains AS rod
                    JOIN reference.research_domains AS d ON d.domain_id = rod.domain_id
                    WHERE rod.research_id = ro.research_id
                ), ''))), 'B') ||
                setweight(to_tsvector('simple', unaccent(coalesce(ro.description, ''))), 'C')
            WHERE ro.research_id = target_research_id;
        END;
        $$;
        """
    )
    op.execute(
        """
        CREATE OR REPLACE FUNCTION core.refresh_research_object_search_vector()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
            PERFORM core.rebuild_research_object_search_vector(NEW.research_id);
            RETURN NEW;
        END;
        $$;
        """
    )
    op.execute(
        """
        CREATE OR REPLACE FUNCTION core.refresh_research_object_search_vector_from_relation()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
            IF TG_OP = 'DELETE' THEN
                PERFORM core.rebuild_research_object_search_vector(OLD.research_id);
                RETURN OLD;
            END IF;
            PERFORM core.rebuild_research_object_search_vector(NEW.research_id);
            RETURN NEW;
        END;
        $$;
        """
    )
    op.execute(
        """
        CREATE OR REPLACE FUNCTION core.refresh_research_object_search_vector_from_keyword()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        DECLARE
            related_research_id uuid;
        BEGIN
            FOR related_research_id IN
                SELECT research_id
                FROM core.research_object_keywords
                WHERE keyword_id = NEW.keyword_id
            LOOP
                PERFORM core.rebuild_research_object_search_vector(related_research_id);
            END LOOP;
            RETURN NEW;
        END;
        $$;
        """
    )
    op.execute(
        """
        CREATE OR REPLACE FUNCTION core.refresh_research_object_search_vector_from_domain()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        DECLARE
            related_research_id uuid;
        BEGIN
            FOR related_research_id IN
                SELECT research_id
                FROM core.research_object_domains
                WHERE domain_id = NEW.domain_id
            LOOP
                PERFORM core.rebuild_research_object_search_vector(related_research_id);
            END LOOP;
            RETURN NEW;
        END;
        $$;
        """
    )
    op.execute(
        """
        DROP TRIGGER IF EXISTS trg_core_research_objects_search_vector ON core.research_objects;
        CREATE TRIGGER trg_core_research_objects_search_vector
        AFTER INSERT OR UPDATE OF title, description, abstract, identifier
        ON core.research_objects
        FOR EACH ROW
        EXECUTE FUNCTION core.refresh_research_object_search_vector();
        """
    )
    for table_name in ("research_object_authors", "research_object_keywords", "research_object_domains"):
        op.execute(
            f"""
            DROP TRIGGER IF EXISTS trg_core_{table_name}_search_vector ON core.{table_name};
            CREATE TRIGGER trg_core_{table_name}_search_vector
            AFTER INSERT OR UPDATE OR DELETE
            ON core.{table_name}
            FOR EACH ROW
            EXECUTE FUNCTION core.refresh_research_object_search_vector_from_relation();
            """
        )
    op.execute(
        """
        DROP TRIGGER IF EXISTS trg_reference_keywords_core_search_vector ON reference.keywords;
        CREATE TRIGGER trg_reference_keywords_core_search_vector
        AFTER UPDATE OF keyword_text, normalized_text
        ON reference.keywords
        FOR EACH ROW
        EXECUTE FUNCTION core.refresh_research_object_search_vector_from_keyword();
        """
    )
    op.execute(
        """
        DROP TRIGGER IF EXISTS trg_reference_research_domains_core_search_vector ON reference.research_domains;
        CREATE TRIGGER trg_reference_research_domains_core_search_vector
        AFTER UPDATE OF domain_code, domain_name, description
        ON reference.research_domains
        FOR EACH ROW
        EXECUTE FUNCTION core.refresh_research_object_search_vector_from_domain();
        """
    )
    op.execute("SELECT core.rebuild_research_object_search_vector(research_id) FROM core.research_objects")


def downgrade() -> None:
    """Downgrade schema."""
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
