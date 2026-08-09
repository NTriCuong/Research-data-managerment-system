WITH documents AS (
    SELECT
        ro.research_id,
        jsonb_strip_nulls(
            jsonb_build_object(
                'schema_version', 1,
                'research_id', ro.research_id::text,
                'source_staging_id', ro.source_staging_id::text,
                'title', ro.title,
                'description', ro.description,
                'abstract', ro.abstract,
                'output_type', jsonb_build_object(
                    'id', ot.output_type_id::text,
                    'code', ot.type_code,
                    'name', ot.type_name
                ),
                'department', jsonb_build_object(
                    'id', department.department_id::text,
                    'code', department.department_code,
                    'name', department.department_name
                ),
                'year', ro.year,
                'start_date', ro.start_date,
                'end_date', ro.end_date,
                'date_issued', ro.date_issued,
                'publisher', ro.publisher,
                'language', ro.language,
                'identifier', ro.identifier,
                'external_url', ro.external_url,
                'source', ro.source,
                'relation', ro.relation,
                'coverage', ro.coverage,
                'rights', ro.rights,
                'access_level', ro.access_level::text,
                'authors', COALESCE(author_data.items, '[]'::jsonb),
                'keywords', COALESCE(keyword_data.items, '[]'::jsonb),
                'domains', COALESCE(domain_data.items, '[]'::jsonb),
                'metadata_quality_score', ro.metadata_quality_score,
                'view_count', ro.view_count,
                'download_count', ro.download_count,
                'version_no', ro.version_no,
                'is_current', ro.is_current,
                'approved_by', ro.approved_by::text,
                'approved_at', ro.approved_at,
                'created_at', ro.created_at,
                'updated_at', ro.updated_at,
                'deleted_at', ro.deleted_at
            )
        ) AS document
    FROM core.research_objects AS ro
    JOIN reference.output_types AS ot
        ON ot.output_type_id = ro.output_type_id
    JOIN reference.departments AS department
        ON department.department_id = ro.department_id
    LEFT JOIN LATERAL (
        SELECT jsonb_agg(
            jsonb_strip_nulls(
                jsonb_build_object(
                    'researcher_id', author.researcher_id::text,
                    'full_name', author.full_name,
                    'email', author.email,
                    'affiliation', author.affiliation,
                    'author_order', author.author_order,
                    'author_role', author.author_role::text
                )
            )
            ORDER BY author.author_order, author.core_author_id
        ) AS items
        FROM core.research_object_authors AS author
        WHERE author.research_id = ro.research_id
    ) AS author_data ON true
    LEFT JOIN LATERAL (
        SELECT jsonb_agg(
            jsonb_strip_nulls(
                jsonb_build_object(
                    'id', keyword.keyword_id::text,
                    'text', keyword.keyword_text,
                    'normalized_text', keyword.normalized_text
                )
            )
            ORDER BY keyword.keyword_text, keyword.keyword_id
        ) AS items
        FROM core.research_object_keywords AS research_keyword
        JOIN reference.keywords AS keyword
            ON keyword.keyword_id = research_keyword.keyword_id
        WHERE research_keyword.research_id = ro.research_id
    ) AS keyword_data ON true
    LEFT JOIN LATERAL (
        SELECT jsonb_agg(
            jsonb_build_object(
                'id', domain.domain_id::text,
                'code', domain.domain_code,
                'name', domain.domain_name
            )
            ORDER BY domain.domain_name, domain.domain_id
        ) AS items
        FROM core.research_object_domains AS research_domain
        JOIN reference.research_domains AS domain
            ON domain.domain_id = research_domain.domain_id
        WHERE research_domain.research_id = ro.research_id
    ) AS domain_data ON true
    WHERE ro.deleted_at IS NULL
      AND ro.is_current IS true
)
SELECT bulk_lines.line
FROM documents
CROSS JOIN LATERAL (
    VALUES
        (
            1,
            jsonb_build_object(
                'index',
                jsonb_build_object(
                    '_index', :'es_index',
                    '_id', documents.research_id::text
                )
            )::text
        ),
        (2, documents.document::text)
) AS bulk_lines(line_order, line)
ORDER BY documents.research_id, bulk_lines.line_order;
