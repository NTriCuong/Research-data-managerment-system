"""initial

Revision ID: 8c689e6ab5e8
Revises:
Create Date: 2026-05-23 02:40:37.782516

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "8c689e6ab5e8"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


SCHEMA_SQL = r"""
-- RDMS combined database script v1.1
-- Run this file on an empty PostgreSQL database.

-- =============================================================
-- RDMS - Research Data Management System
-- PostgreSQL Database Schema
-- Version: 1.1
-- Scope: Graduation thesis MVP for 2 students / 12 weeks
-- Author: Prepared for RDMS student implementation
-- =============================================================

-- 0. Extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS unaccent;

-- 1. Schemas
CREATE SCHEMA IF NOT EXISTS app;
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS reference;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS log;

-- 2. Enum types
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_status' AND typnamespace = 'app'::regnamespace) THEN
        CREATE TYPE app.user_status AS ENUM ('active', 'disabled');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'workflow_status' AND typnamespace = 'app'::regnamespace) THEN
        CREATE TYPE app.workflow_status AS ENUM (
            'draft',
            'pending_review',
            'revision_required',
            'pending_approval',
            'approved',
            'rejected'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'access_level' AND typnamespace = 'app'::regnamespace) THEN
        CREATE TYPE app.access_level AS ENUM ('private', 'internal', 'public');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'author_role' AND typnamespace = 'app'::regnamespace) THEN
        CREATE TYPE app.author_role AS ENUM (
            'creator',
            'contributor',
            'supervisor',
            'student_member',
            'corresponding_author'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'file_status' AND typnamespace = 'app'::regnamespace) THEN
        CREATE TYPE app.file_status AS ENUM ('active', 'replaced', 'deleted');
    END IF;
END $$;

-- 3. Shared utility function for updated_at
CREATE OR REPLACE FUNCTION app.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =============================================================
-- AUTH SCHEMA
-- =============================================================

CREATE TABLE IF NOT EXISTS auth.roles (
    role_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_code VARCHAR(50) NOT NULL UNIQUE,
    role_name VARCHAR(100) NOT NULL,
    description TEXT,
    is_system_role BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE auth.roles IS 'RBAC roles for RDMS users.';

-- =============================================================
-- REFERENCE SCHEMA
-- =============================================================

CREATE TABLE IF NOT EXISTS reference.departments (
    department_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    department_code VARCHAR(50) NOT NULL UNIQUE,
    department_name VARCHAR(255) NOT NULL,
    parent_department_id UUID REFERENCES reference.departments(department_id),
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS reference.output_types (
    output_type_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_code VARCHAR(50) NOT NULL UNIQUE,
    type_name VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS reference.research_domains (
    domain_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain_code VARCHAR(50) NOT NULL UNIQUE,
    domain_name VARCHAR(255) NOT NULL,
    parent_domain_id UUID REFERENCES reference.research_domains(domain_id),
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS reference.keywords (
    keyword_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    keyword_text VARCHAR(255) NOT NULL UNIQUE,
    normalized_text VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS reference.researchers (
    researcher_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    orcid VARCHAR(50),
    department_id UUID REFERENCES reference.departments(department_id),
    academic_title VARCHAR(100),
    researcher_code VARCHAR(100),
    is_internal BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ
);

COMMENT ON TABLE reference.departments IS 'University units such as faculty, department, center, office.';
COMMENT ON TABLE reference.output_types IS 'Research object types such as project, publication, dataset, evidence document.';
COMMENT ON TABLE reference.research_domains IS 'Research domains used for classification and reporting.';
COMMENT ON TABLE reference.keywords IS 'Controlled or semi-controlled keywords for research metadata.';
COMMENT ON TABLE reference.researchers IS 'Researchers, lecturers, students or external contributors.';

CREATE INDEX IF NOT EXISTS idx_departments_parent ON reference.departments(parent_department_id);
CREATE INDEX IF NOT EXISTS idx_domains_parent ON reference.research_domains(parent_domain_id);
CREATE INDEX IF NOT EXISTS idx_keywords_text ON reference.keywords(keyword_text);
CREATE INDEX IF NOT EXISTS idx_researchers_department_id ON reference.researchers(department_id);
CREATE INDEX IF NOT EXISTS idx_researchers_full_name ON reference.researchers(full_name);

DROP TRIGGER IF EXISTS trg_departments_updated_at ON reference.departments;
CREATE TRIGGER trg_departments_updated_at
BEFORE UPDATE ON reference.departments
FOR EACH ROW EXECUTE FUNCTION app.set_updated_at();

DROP TRIGGER IF EXISTS trg_output_types_updated_at ON reference.output_types;
CREATE TRIGGER trg_output_types_updated_at
BEFORE UPDATE ON reference.output_types
FOR EACH ROW EXECUTE FUNCTION app.set_updated_at();

DROP TRIGGER IF EXISTS trg_domains_updated_at ON reference.research_domains;
CREATE TRIGGER trg_domains_updated_at
BEFORE UPDATE ON reference.research_domains
FOR EACH ROW EXECUTE FUNCTION app.set_updated_at();

DROP TRIGGER IF EXISTS trg_researchers_updated_at ON reference.researchers;
CREATE TRIGGER trg_researchers_updated_at
BEFORE UPDATE ON reference.researchers
FOR EACH ROW EXECUTE FUNCTION app.set_updated_at();

-- =============================================================
-- AUTH USERS AFTER REFERENCE DEPARTMENTS
-- =============================================================

CREATE TABLE IF NOT EXISTS auth.users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash TEXT NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role_id UUID NOT NULL REFERENCES auth.roles(role_id),
    department_id UUID REFERENCES reference.departments(department_id),
    status app.user_status NOT NULL DEFAULT 'active',
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ,
    deleted_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS auth.refresh_tokens (
    token_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(user_id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL,
    issued_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ,
    ip_address INET,
    user_agent TEXT
);

COMMENT ON TABLE auth.users IS 'RDMS user accounts. Passwords must be stored as hashes only.';
COMMENT ON TABLE auth.refresh_tokens IS 'Refresh token store for JWT-based authentication.';

CREATE INDEX IF NOT EXISTS idx_users_role_id ON auth.users(role_id);
CREATE INDEX IF NOT EXISTS idx_users_department_id ON auth.users(department_id);
CREATE INDEX IF NOT EXISTS idx_users_status ON auth.users(status);

-- v1.1: partial unique indexes avoid soft-delete conflicts.
-- A deleted user can keep the old username/email while a new active user can reuse them.
CREATE UNIQUE INDEX IF NOT EXISTS uq_users_username_active
ON auth.users(username)
WHERE deleted_at IS NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_users_email_active
ON auth.users(email)
WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON auth.refresh_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires ON auth.refresh_tokens(expires_at);

DROP TRIGGER IF EXISTS trg_users_updated_at ON auth.users;
CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON auth.users
FOR EACH ROW EXECUTE FUNCTION app.set_updated_at();

-- =============================================================
-- STAGING SCHEMA
-- =============================================================

CREATE TABLE IF NOT EXISTS staging.research_objects (
    staging_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    title TEXT NOT NULL,
    description TEXT,
    abstract TEXT,

    output_type_id UUID NOT NULL REFERENCES reference.output_types(output_type_id),
    department_id UUID NOT NULL REFERENCES reference.departments(department_id),

    year INTEGER CHECK (year BETWEEN 1900 AND 2100),
    start_date DATE,
    end_date DATE,
    date_issued DATE,

    publisher VARCHAR(255),
    language VARCHAR(50) DEFAULT 'vi',
    identifier VARCHAR(255),
    external_url TEXT,
    source TEXT,
    relation TEXT,
    coverage TEXT,
    rights TEXT,

    access_level app.access_level NOT NULL DEFAULT 'internal',
    workflow_status app.workflow_status NOT NULL DEFAULT 'draft',

    -- v1.1: used by FR-CORE-04 to update an already approved core record through staging workflow.
    source_core_research_id UUID,
    update_reason TEXT,

    metadata_quality_score NUMERIC(5,2) DEFAULT 0,
    metadata_quality_detail JSONB,

    created_by UUID NOT NULL REFERENCES auth.users(user_id),
    submitted_by UUID REFERENCES auth.users(user_id),
    submitted_at TIMESTAMPTZ,

    reviewed_by UUID REFERENCES auth.users(user_id),
    reviewed_at TIMESTAMPTZ,

    approved_by UUID REFERENCES auth.users(user_id),
    approved_at TIMESTAMPTZ,

    rejection_reason TEXT,
    revision_note TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ,
    deleted_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS staging.research_object_authors (
    staging_author_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    staging_id UUID NOT NULL REFERENCES staging.research_objects(staging_id) ON DELETE CASCADE,
    researcher_id UUID REFERENCES reference.researchers(researcher_id),

    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    affiliation VARCHAR(255),
    author_order INTEGER NOT NULL DEFAULT 1,
    author_role app.author_role NOT NULL DEFAULT 'creator',

    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_staging_author_order UNIQUE (staging_id, author_order)
);

CREATE TABLE IF NOT EXISTS staging.research_object_domains (
    staging_id UUID NOT NULL REFERENCES staging.research_objects(staging_id) ON DELETE CASCADE,
    domain_id UUID NOT NULL REFERENCES reference.research_domains(domain_id),
    PRIMARY KEY (staging_id, domain_id)
);

CREATE TABLE IF NOT EXISTS staging.research_object_keywords (
    staging_id UUID NOT NULL REFERENCES staging.research_objects(staging_id) ON DELETE CASCADE,
    keyword_id UUID NOT NULL REFERENCES reference.keywords(keyword_id),
    PRIMARY KEY (staging_id, keyword_id)
);

CREATE TABLE IF NOT EXISTS staging.file_attachments (
    file_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    staging_id UUID NOT NULL REFERENCES staging.research_objects(staging_id) ON DELETE CASCADE,

    original_filename VARCHAR(500) NOT NULL,
    stored_filename VARCHAR(500) NOT NULL,
    storage_path TEXT NOT NULL,

    mime_type VARCHAR(100) NOT NULL,
    file_extension VARCHAR(20),
    file_size_bytes BIGINT NOT NULL CHECK (file_size_bytes > 0),
    checksum_sha256 VARCHAR(128),

    file_status app.file_status NOT NULL DEFAULT 'active',
    uploaded_by UUID NOT NULL REFERENCES auth.users(user_id),
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    access_level app.access_level NOT NULL DEFAULT 'internal'
);

COMMENT ON TABLE staging.research_objects IS 'Temporary research metadata records before formal approval.';
COMMENT ON TABLE staging.file_attachments IS 'Attachment metadata for staging research objects. Physical files are stored outside the database.';

CREATE INDEX IF NOT EXISTS idx_staging_status ON staging.research_objects(workflow_status);
CREATE INDEX IF NOT EXISTS idx_staging_department ON staging.research_objects(department_id);
CREATE INDEX IF NOT EXISTS idx_staging_output_type ON staging.research_objects(output_type_id);
CREATE INDEX IF NOT EXISTS idx_staging_year ON staging.research_objects(year);
CREATE INDEX IF NOT EXISTS idx_staging_created_by ON staging.research_objects(created_by);
CREATE INDEX IF NOT EXISTS idx_staging_authors_staging_id ON staging.research_object_authors(staging_id);
CREATE INDEX IF NOT EXISTS idx_staging_files_staging_id ON staging.file_attachments(staging_id);

DROP TRIGGER IF EXISTS trg_staging_research_updated_at ON staging.research_objects;
CREATE TRIGGER trg_staging_research_updated_at
BEFORE UPDATE ON staging.research_objects
FOR EACH ROW EXECUTE FUNCTION app.set_updated_at();

-- =============================================================
-- CORE SCHEMA
-- =============================================================

CREATE TABLE IF NOT EXISTS core.research_objects (
    research_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_staging_id UUID UNIQUE REFERENCES staging.research_objects(staging_id),

    title TEXT NOT NULL,
    description TEXT,
    abstract TEXT,

    output_type_id UUID NOT NULL REFERENCES reference.output_types(output_type_id),
    department_id UUID NOT NULL REFERENCES reference.departments(department_id),

    year INTEGER CHECK (year BETWEEN 1900 AND 2100),
    start_date DATE,
    end_date DATE,
    date_issued DATE,

    publisher VARCHAR(255),
    language VARCHAR(50) DEFAULT 'vi',
    identifier VARCHAR(255),
    external_url TEXT,
    source TEXT,
    relation TEXT,
    coverage TEXT,
    rights TEXT,

    access_level app.access_level NOT NULL DEFAULT 'internal',
    metadata_quality_score NUMERIC(5,2) DEFAULT 0,
    metadata_quality_detail JSONB,

    -- v1.1: denormalized FTS vector. It is refreshed by triggers/functions and covers
    -- title, abstract, authors, keywords, domains, department and output type.
    search_vector TSVECTOR,

    version_no INTEGER NOT NULL DEFAULT 1,
    is_current BOOLEAN NOT NULL DEFAULT TRUE,

    approved_by UUID NOT NULL REFERENCES auth.users(user_id),
    approved_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ,
    deleted_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS core.research_object_authors (
    core_author_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    research_id UUID NOT NULL REFERENCES core.research_objects(research_id) ON DELETE CASCADE,
    researcher_id UUID REFERENCES reference.researchers(researcher_id),

    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    affiliation VARCHAR(255),
    author_order INTEGER NOT NULL DEFAULT 1,
    author_role app.author_role NOT NULL DEFAULT 'creator',

    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_core_author_order UNIQUE (research_id, author_order)
);

CREATE TABLE IF NOT EXISTS core.research_object_domains (
    research_id UUID NOT NULL REFERENCES core.research_objects(research_id) ON DELETE CASCADE,
    domain_id UUID NOT NULL REFERENCES reference.research_domains(domain_id),
    PRIMARY KEY (research_id, domain_id)
);

CREATE TABLE IF NOT EXISTS core.research_object_keywords (
    research_id UUID NOT NULL REFERENCES core.research_objects(research_id) ON DELETE CASCADE,
    keyword_id UUID NOT NULL REFERENCES reference.keywords(keyword_id),
    PRIMARY KEY (research_id, keyword_id)
);

CREATE TABLE IF NOT EXISTS core.file_attachments (
    file_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    research_id UUID NOT NULL REFERENCES core.research_objects(research_id) ON DELETE CASCADE,

    original_filename VARCHAR(500) NOT NULL,
    stored_filename VARCHAR(500) NOT NULL,
    storage_path TEXT NOT NULL,

    mime_type VARCHAR(100) NOT NULL,
    file_extension VARCHAR(20),
    file_size_bytes BIGINT NOT NULL CHECK (file_size_bytes > 0),
    checksum_sha256 VARCHAR(128),

    file_status app.file_status NOT NULL DEFAULT 'active',
    uploaded_by UUID NOT NULL REFERENCES auth.users(user_id),
    uploaded_at TIMESTAMPTZ NOT NULL,

    access_level app.access_level NOT NULL DEFAULT 'internal'
);

CREATE TABLE IF NOT EXISTS core.metadata_versions (
    version_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    research_id UUID NOT NULL REFERENCES core.research_objects(research_id) ON DELETE CASCADE,

    version_no INTEGER NOT NULL,
    metadata_snapshot JSONB NOT NULL,

    change_reason TEXT,
    created_by UUID NOT NULL REFERENCES auth.users(user_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_metadata_version UNIQUE (research_id, version_no)
);

COMMENT ON TABLE core.research_objects IS 'Approved official research metadata records.';
COMMENT ON TABLE core.metadata_versions IS 'Metadata snapshots for versioning and traceability.';

-- v1.1: staging records may represent update requests for an approved core record.
ALTER TABLE staging.research_objects
ADD CONSTRAINT fk_staging_source_core_research
FOREIGN KEY (source_core_research_id)
REFERENCES core.research_objects(research_id);

CREATE INDEX IF NOT EXISTS idx_core_department ON core.research_objects(department_id);
CREATE INDEX IF NOT EXISTS idx_core_output_type ON core.research_objects(output_type_id);
CREATE INDEX IF NOT EXISTS idx_core_year ON core.research_objects(year);
CREATE INDEX IF NOT EXISTS idx_core_access_level ON core.research_objects(access_level);
CREATE INDEX IF NOT EXISTS idx_core_approved_at ON core.research_objects(approved_at);
CREATE INDEX IF NOT EXISTS idx_core_authors_research_id ON core.research_object_authors(research_id);
CREATE INDEX IF NOT EXISTS idx_core_files_research_id ON core.file_attachments(research_id);
CREATE INDEX IF NOT EXISTS idx_metadata_versions_research_id ON core.metadata_versions(research_id);

-- v1.1: unique active identifier only when identifier is present.
CREATE UNIQUE INDEX IF NOT EXISTS uq_core_identifier_active
ON core.research_objects(lower(identifier))
WHERE identifier IS NOT NULL AND deleted_at IS NULL;

-- v1.1: full-text search vector index.
CREATE INDEX IF NOT EXISTS idx_core_research_fts
ON core.research_objects
USING GIN (search_vector);

DROP TRIGGER IF EXISTS trg_core_research_updated_at ON core.research_objects;
CREATE TRIGGER trg_core_research_updated_at
BEFORE UPDATE ON core.research_objects
FOR EACH ROW EXECUTE FUNCTION app.set_updated_at();

-- =============================================================
-- LOG SCHEMA
-- =============================================================

CREATE TABLE IF NOT EXISTS log.workflow_history (
    workflow_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    staging_id UUID REFERENCES staging.research_objects(staging_id),
    research_id UUID REFERENCES core.research_objects(research_id),

    from_status app.workflow_status,
    to_status app.workflow_status NOT NULL,

    action_code VARCHAR(100) NOT NULL,
    action_note TEXT,

    performed_by UUID NOT NULL REFERENCES auth.users(user_id),
    performed_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    ip_address INET,
    user_agent TEXT,

    -- v1.1: workflow event must point to at least one target record.
    CONSTRAINT ck_workflow_target_required
        CHECK (staging_id IS NOT NULL OR research_id IS NOT NULL),

    -- v1.1: prevent accidental no-op transition except explicit version/update actions.
    CONSTRAINT ck_workflow_status_change
        CHECK (from_status IS NULL OR from_status <> to_status OR action_code IN ('UPDATE_APPROVED_RECORD', 'CREATE_METADATA_VERSION'))
);

CREATE TABLE IF NOT EXISTS log.audit_logs (
    audit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    actor_user_id UUID REFERENCES auth.users(user_id),
    action_code VARCHAR(100) NOT NULL,

    target_schema VARCHAR(100),
    target_table VARCHAR(100),
    target_id UUID,

    old_value JSONB,
    new_value JSONB,

    result VARCHAR(50) NOT NULL DEFAULT 'success',
    message TEXT,

    ip_address INET,
    user_agent TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS log.login_logs (
    login_log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID REFERENCES auth.users(user_id),
    username_attempted VARCHAR(255),

    login_result VARCHAR(50) NOT NULL,
    failure_reason TEXT,

    ip_address INET,
    user_agent TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE log.workflow_history IS 'Workflow transition history for review and approval process.';
COMMENT ON TABLE log.audit_logs IS 'Audit trail for important system and data changes.';
COMMENT ON TABLE log.login_logs IS 'Login success/failure records.';

CREATE INDEX IF NOT EXISTS idx_workflow_staging_id ON log.workflow_history(staging_id);
CREATE INDEX IF NOT EXISTS idx_workflow_research_id ON log.workflow_history(research_id);
CREATE INDEX IF NOT EXISTS idx_workflow_performed_by ON log.workflow_history(performed_by);
CREATE INDEX IF NOT EXISTS idx_workflow_performed_at ON log.workflow_history(performed_at);
CREATE INDEX IF NOT EXISTS idx_audit_actor ON log.audit_logs(actor_user_id);
CREATE INDEX IF NOT EXISTS idx_audit_action_code ON log.audit_logs(action_code);
CREATE INDEX IF NOT EXISTS idx_audit_target ON log.audit_logs(target_schema, target_table, target_id);
CREATE INDEX IF NOT EXISTS idx_audit_created_at ON log.audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_login_logs_user_id ON log.login_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_login_logs_created_at ON log.login_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_login_logs_result ON log.login_logs(login_result);

-- =============================================================
-- METADATA QUALITY UTILITY FUNCTIONS
-- =============================================================

CREATE OR REPLACE FUNCTION app.compute_staging_metadata_quality(p_staging_id UUID)
RETURNS JSONB AS $$
DECLARE
    v_record staging.research_objects%ROWTYPE;
    v_author_count INTEGER := 0;
    v_domain_count INTEGER := 0;
    v_keyword_count INTEGER := 0;
    v_file_count INTEGER := 0;
    v_completeness NUMERIC := 0;
    v_validity NUMERIC := 0;
    v_evidence NUMERIC := 0;
    v_traceability NUMERIC := 0;
    v_total NUMERIC := 0;
BEGIN
    SELECT * INTO v_record
    FROM staging.research_objects
    WHERE staging_id = p_staging_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Staging record % not found', p_staging_id;
    END IF;

    SELECT COUNT(*) INTO v_author_count FROM staging.research_object_authors WHERE staging_id = p_staging_id;
    SELECT COUNT(*) INTO v_domain_count FROM staging.research_object_domains WHERE staging_id = p_staging_id;
    SELECT COUNT(*) INTO v_keyword_count FROM staging.research_object_keywords WHERE staging_id = p_staging_id;
    SELECT COUNT(*) INTO v_file_count FROM staging.file_attachments WHERE staging_id = p_staging_id AND file_status = 'active';

    -- Completeness: max 50
    v_completeness :=
        (CASE WHEN v_record.title IS NOT NULL AND length(trim(v_record.title)) > 0 THEN 8 ELSE 0 END) +
        (CASE WHEN v_record.description IS NOT NULL AND length(trim(v_record.description)) > 0 THEN 7 ELSE 0 END) +
        (CASE WHEN v_record.output_type_id IS NOT NULL THEN 6 ELSE 0 END) +
        (CASE WHEN v_record.department_id IS NOT NULL THEN 6 ELSE 0 END) +
        (CASE WHEN v_record.year IS NOT NULL THEN 6 ELSE 0 END) +
        (CASE WHEN v_author_count > 0 THEN 7 ELSE 0 END) +
        (CASE WHEN v_domain_count > 0 THEN 5 ELSE 0 END) +
        (CASE WHEN v_keyword_count > 0 THEN 5 ELSE 0 END);

    -- Validity: max 25
    -- v1.1 fix: year IS NULL must NOT receive positive validity score.
    v_validity :=
        (CASE WHEN v_record.year IS NOT NULL AND v_record.year BETWEEN 1900 AND 2100 THEN 8 ELSE 0 END) +
        (CASE WHEN v_record.language IS NULL OR length(v_record.language) <= 50 THEN 4 ELSE 0 END) +
        (CASE WHEN v_record.external_url IS NULL OR v_record.external_url ~* '^https?://' THEN 5 ELSE 0 END) +
        (CASE WHEN v_record.access_level IS NOT NULL THEN 4 ELSE 0 END) +
        (CASE WHEN v_record.workflow_status IS NOT NULL THEN 4 ELSE 0 END);

    -- Evidence: max 15
    v_evidence := CASE WHEN v_file_count > 0 THEN 15 ELSE 0 END;

    -- Traceability: max 10
    v_traceability :=
        (CASE WHEN v_record.created_by IS NOT NULL THEN 4 ELSE 0 END) +
        (CASE WHEN v_record.created_at IS NOT NULL THEN 3 ELSE 0 END) +
        (CASE WHEN v_record.workflow_status IS NOT NULL THEN 3 ELSE 0 END);

    v_total := v_completeness + v_validity + v_evidence + v_traceability;

    RETURN jsonb_build_object(
        'total', v_total,
        'completeness', v_completeness,
        'validity', v_validity,
        'evidence', v_evidence,
        'traceability', v_traceability,
        'author_count', v_author_count,
        'domain_count', v_domain_count,
        'keyword_count', v_keyword_count,
        'file_count', v_file_count,
        'year_valid', (v_record.year IS NOT NULL AND v_record.year BETWEEN 1900 AND 2100)
    );
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION app.refresh_staging_metadata_quality(p_staging_id UUID)
RETURNS NUMERIC AS $$
DECLARE
    v_quality JSONB;
    v_total NUMERIC;
BEGIN
    v_quality := app.compute_staging_metadata_quality(p_staging_id);
    v_total := (v_quality ->> 'total')::NUMERIC;

    UPDATE staging.research_objects
    SET metadata_quality_score = v_total,
        metadata_quality_detail = v_quality,
        updated_at = now()
    WHERE staging_id = p_staging_id;

    RETURN v_total;
END;
$$ LANGUAGE plpgsql;

-- =============================================================
-- v1.1 FULL-TEXT SEARCH VECTOR FUNCTIONS
-- Covers core metadata, authors, keywords, research domains, department and output type.
-- Vietnamese text is normalized with unaccent before creating tsvector.
-- =============================================================

CREATE OR REPLACE FUNCTION app.refresh_core_search_vector(p_research_id UUID)
RETURNS VOID AS $$
DECLARE
    v_document TEXT;
BEGIN
    SELECT concat_ws(' ',
        r.title,
        r.description,
        r.abstract,
        r.publisher,
        r.identifier,
        r.year::TEXT,
        d.department_name,
        ot.type_name,
        string_agg(DISTINCT a.full_name, ' '),
        string_agg(DISTINCT a.email, ' '),
        string_agg(DISTINCT k.keyword_text, ' '),
        string_agg(DISTINCT rd.domain_name, ' ')
    )
    INTO v_document
    FROM core.research_objects r
    LEFT JOIN reference.departments d ON d.department_id = r.department_id
    LEFT JOIN reference.output_types ot ON ot.output_type_id = r.output_type_id
    LEFT JOIN core.research_object_authors a ON a.research_id = r.research_id
    LEFT JOIN core.research_object_keywords rok ON rok.research_id = r.research_id
    LEFT JOIN reference.keywords k ON k.keyword_id = rok.keyword_id
    LEFT JOIN core.research_object_domains rod ON rod.research_id = r.research_id
    LEFT JOIN reference.research_domains rd ON rd.domain_id = rod.domain_id
    WHERE r.research_id = p_research_id
    GROUP BY r.research_id, d.department_name, ot.type_name;

    UPDATE core.research_objects
    SET search_vector = to_tsvector('simple', unaccent(coalesce(v_document, '')))
    WHERE research_id = p_research_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION app.trg_refresh_core_search_vector()
RETURNS TRIGGER AS $$
DECLARE
    v_research_id UUID;
BEGIN
    IF TG_OP = 'DELETE' THEN
        v_research_id := OLD.research_id;
    ELSE
        v_research_id := NEW.research_id;
    END IF;

    IF v_research_id IS NOT NULL THEN
        PERFORM app.refresh_core_search_vector(v_research_id);
    END IF;

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_core_refresh_search_vector_base ON core.research_objects;
CREATE TRIGGER trg_core_refresh_search_vector_base
AFTER INSERT OR UPDATE OF title, description, abstract, publisher, identifier, year, department_id, output_type_id
ON core.research_objects
FOR EACH ROW EXECUTE FUNCTION app.trg_refresh_core_search_vector();

DROP TRIGGER IF EXISTS trg_core_authors_refresh_search_vector ON core.research_object_authors;
CREATE TRIGGER trg_core_authors_refresh_search_vector
AFTER INSERT OR UPDATE OR DELETE ON core.research_object_authors
FOR EACH ROW EXECUTE FUNCTION app.trg_refresh_core_search_vector();

DROP TRIGGER IF EXISTS trg_core_keywords_refresh_search_vector ON core.research_object_keywords;
CREATE TRIGGER trg_core_keywords_refresh_search_vector
AFTER INSERT OR UPDATE OR DELETE ON core.research_object_keywords
FOR EACH ROW EXECUTE FUNCTION app.trg_refresh_core_search_vector();

DROP TRIGGER IF EXISTS trg_core_domains_refresh_search_vector ON core.research_object_domains;
CREATE TRIGGER trg_core_domains_refresh_search_vector
AFTER INSERT OR UPDATE OR DELETE ON core.research_object_domains
FOR EACH ROW EXECUTE FUNCTION app.trg_refresh_core_search_vector();

-- =============================================================
-- APPROVAL FUNCTION
-- This function can be called by backend after approver confirms approval.
-- =============================================================

CREATE OR REPLACE FUNCTION app.approve_staging_record(
    p_staging_id UUID,
    p_approver_user_id UUID,
    p_action_note TEXT DEFAULT 'Approved metadata record'
)
RETURNS UUID AS $$
DECLARE
    v_staging staging.research_objects%ROWTYPE;
    v_old_status app.workflow_status;
    v_research_id UUID;
    v_old_snapshot JSONB;
    v_snapshot JSONB;
    v_next_version INTEGER;
    v_action_code VARCHAR(100);
BEGIN
    SELECT * INTO v_staging
    FROM staging.research_objects
    WHERE staging_id = p_staging_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Staging record % not found', p_staging_id;
    END IF;

    v_old_status := v_staging.workflow_status;

    IF v_old_status <> 'pending_approval' THEN
        RAISE EXCEPTION 'Record must be in pending_approval status. Current status: %', v_old_status;
    END IF;

    PERFORM app.refresh_staging_metadata_quality(p_staging_id);

    IF v_staging.source_core_research_id IS NULL THEN
        v_action_code := 'APPROVE_RECORD';

        INSERT INTO core.research_objects (
            source_staging_id,
            title,
            description,
            abstract,
            output_type_id,
            department_id,
            year,
            start_date,
            end_date,
            date_issued,
            publisher,
            language,
            identifier,
            external_url,
            source,
            relation,
            coverage,
            rights,
            access_level,
            metadata_quality_score,
            metadata_quality_detail,
            approved_by,
            approved_at
        )
        SELECT
            staging_id,
            title,
            description,
            abstract,
            output_type_id,
            department_id,
            year,
            start_date,
            end_date,
            date_issued,
            publisher,
            language,
            identifier,
            external_url,
            source,
            relation,
            coverage,
            rights,
            access_level,
            metadata_quality_score,
            metadata_quality_detail,
            p_approver_user_id,
            now()
        FROM staging.research_objects
        WHERE staging_id = p_staging_id
        RETURNING research_id INTO v_research_id;
    ELSE
        v_action_code := 'APPROVE_UPDATE_RECORD';
        v_research_id := v_staging.source_core_research_id;

        SELECT to_jsonb(r.*) INTO v_old_snapshot
        FROM core.research_objects r
        WHERE r.research_id = v_research_id
        FOR UPDATE;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'Source core record % not found', v_research_id;
        END IF;

        SELECT COALESCE(MAX(version_no), 0) + 1 INTO v_next_version
        FROM core.metadata_versions
        WHERE research_id = v_research_id;

        UPDATE core.research_objects c
        SET
            source_staging_id = p_staging_id,
            title = s.title,
            description = s.description,
            abstract = s.abstract,
            output_type_id = s.output_type_id,
            department_id = s.department_id,
            year = s.year,
            start_date = s.start_date,
            end_date = s.end_date,
            date_issued = s.date_issued,
            publisher = s.publisher,
            language = s.language,
            identifier = s.identifier,
            external_url = s.external_url,
            source = s.source,
            relation = s.relation,
            coverage = s.coverage,
            rights = s.rights,
            access_level = s.access_level,
            metadata_quality_score = s.metadata_quality_score,
            metadata_quality_detail = s.metadata_quality_detail,
            version_no = v_next_version,
            approved_by = p_approver_user_id,
            approved_at = now(),
            updated_at = now()
        FROM staging.research_objects s
        WHERE c.research_id = v_research_id
          AND s.staging_id = p_staging_id;

        DELETE FROM core.research_object_authors WHERE research_id = v_research_id;
        DELETE FROM core.research_object_domains WHERE research_id = v_research_id;
        DELETE FROM core.research_object_keywords WHERE research_id = v_research_id;
        DELETE FROM core.file_attachments WHERE research_id = v_research_id;
    END IF;

    INSERT INTO core.research_object_authors (
        research_id,
        researcher_id,
        full_name,
        email,
        affiliation,
        author_order,
        author_role
    )
    SELECT
        v_research_id,
        researcher_id,
        full_name,
        email,
        affiliation,
        author_order,
        author_role
    FROM staging.research_object_authors
    WHERE staging_id = p_staging_id;

    INSERT INTO core.research_object_domains (research_id, domain_id)
    SELECT v_research_id, domain_id
    FROM staging.research_object_domains
    WHERE staging_id = p_staging_id;

    INSERT INTO core.research_object_keywords (research_id, keyword_id)
    SELECT v_research_id, keyword_id
    FROM staging.research_object_keywords
    WHERE staging_id = p_staging_id;

    INSERT INTO core.file_attachments (
        research_id,
        original_filename,
        stored_filename,
        storage_path,
        mime_type,
        file_extension,
        file_size_bytes,
        checksum_sha256,
        file_status,
        uploaded_by,
        uploaded_at,
        access_level
    )
    SELECT
        v_research_id,
        original_filename,
        stored_filename,
        storage_path,
        mime_type,
        file_extension,
        file_size_bytes,
        checksum_sha256,
        file_status,
        uploaded_by,
        uploaded_at,
        access_level
    FROM staging.file_attachments
    WHERE staging_id = p_staging_id
      AND file_status = 'active';

    PERFORM app.refresh_core_search_vector(v_research_id);

    SELECT to_jsonb(r.*) INTO v_snapshot
    FROM core.research_objects r
    WHERE r.research_id = v_research_id;

    IF v_staging.source_core_research_id IS NULL THEN
        v_next_version := 1;
    ELSE
        SELECT version_no INTO v_next_version
        FROM core.research_objects
        WHERE research_id = v_research_id;
    END IF;

    INSERT INTO core.metadata_versions (
        research_id,
        version_no,
        metadata_snapshot,
        change_reason,
        created_by
    )
    VALUES (
        v_research_id,
        v_next_version,
        v_snapshot,
        COALESCE(v_staging.update_reason, p_action_note, 'Approved metadata version'),
        p_approver_user_id
    );

    UPDATE staging.research_objects
    SET workflow_status = 'approved',
        approved_by = p_approver_user_id,
        approved_at = now(),
        updated_at = now()
    WHERE staging_id = p_staging_id;

    INSERT INTO log.workflow_history (
        staging_id,
        research_id,
        from_status,
        to_status,
        action_code,
        action_note,
        performed_by
    )
    VALUES (
        p_staging_id,
        v_research_id,
        v_old_status,
        'approved',
        v_action_code,
        p_action_note,
        p_approver_user_id
    );

    INSERT INTO log.audit_logs (
        actor_user_id,
        action_code,
        target_schema,
        target_table,
        target_id,
        old_value,
        new_value,
        result,
        message
    )
    VALUES (
        p_approver_user_id,
        v_action_code,
        'core',
        'research_objects',
        v_research_id,
        v_old_snapshot,
        v_snapshot,
        'success',
        'Staging record approved and synchronized to core schema'
    );

    RETURN v_research_id;
END;
$$ LANGUAGE plpgsql;

-- =============================================================
-- v1.1 FR-CORE-04 SUPPORT: CREATE UPDATE REQUEST FROM APPROVED CORE RECORD
-- The update request is created in staging and must pass review/approval again.
-- =============================================================

CREATE OR REPLACE FUNCTION app.create_core_update_request(
    p_research_id UUID,
    p_created_by UUID,
    p_update_reason TEXT DEFAULT 'Update approved metadata record'
)
RETURNS UUID AS $$
DECLARE
    v_staging_id UUID;
BEGIN
    INSERT INTO staging.research_objects (
        title,
        description,
        abstract,
        output_type_id,
        department_id,
        year,
        start_date,
        end_date,
        date_issued,
        publisher,
        language,
        identifier,
        external_url,
        source,
        relation,
        coverage,
        rights,
        access_level,
        workflow_status,
        source_core_research_id,
        update_reason,
        metadata_quality_score,
        metadata_quality_detail,
        created_by
    )
    SELECT
        title,
        description,
        abstract,
        output_type_id,
        department_id,
        year,
        start_date,
        end_date,
        date_issued,
        publisher,
        language,
        identifier,
        external_url,
        source,
        relation,
        coverage,
        rights,
        access_level,
        'draft',
        research_id,
        p_update_reason,
        metadata_quality_score,
        metadata_quality_detail,
        p_created_by
    FROM core.research_objects
    WHERE research_id = p_research_id
      AND deleted_at IS NULL
    RETURNING staging_id INTO v_staging_id;

    IF v_staging_id IS NULL THEN
        RAISE EXCEPTION 'Approved core record % not found', p_research_id;
    END IF;

    INSERT INTO staging.research_object_authors (
        staging_id, researcher_id, full_name, email, affiliation, author_order, author_role
    )
    SELECT v_staging_id, researcher_id, full_name, email, affiliation, author_order, author_role
    FROM core.research_object_authors
    WHERE research_id = p_research_id;

    INSERT INTO staging.research_object_domains (staging_id, domain_id)
    SELECT v_staging_id, domain_id
    FROM core.research_object_domains
    WHERE research_id = p_research_id;

    INSERT INTO staging.research_object_keywords (staging_id, keyword_id)
    SELECT v_staging_id, keyword_id
    FROM core.research_object_keywords
    WHERE research_id = p_research_id;

    INSERT INTO staging.file_attachments (
        staging_id,
        original_filename,
        stored_filename,
        storage_path,
        mime_type,
        file_extension,
        file_size_bytes,
        checksum_sha256,
        file_status,
        uploaded_by,
        uploaded_at,
        access_level
    )
    SELECT
        v_staging_id,
        original_filename,
        stored_filename,
        storage_path,
        mime_type,
        file_extension,
        file_size_bytes,
        checksum_sha256,
        file_status,
        uploaded_by,
        uploaded_at,
        access_level
    FROM core.file_attachments
    WHERE research_id = p_research_id
      AND file_status = 'active';

    INSERT INTO log.workflow_history (
        staging_id,
        research_id,
        from_status,
        to_status,
        action_code,
        action_note,
        performed_by
    )
    VALUES (
        v_staging_id,
        p_research_id,
        NULL,
        'draft',
        'CREATE_UPDATE_REQUEST',
        p_update_reason,
        p_created_by
    );

    RETURN v_staging_id;
END;
$$ LANGUAGE plpgsql;

-- =============================================================
-- DASHBOARD VIEWS
-- =============================================================

CREATE OR REPLACE VIEW core.v_research_by_year AS
SELECT
    year,
    COUNT(*) AS total_records
FROM core.research_objects
WHERE deleted_at IS NULL
GROUP BY year
ORDER BY year DESC;

CREATE OR REPLACE VIEW core.v_research_by_department AS
SELECT
    d.department_id,
    d.department_name,
    COUNT(r.research_id) AS total_records
FROM reference.departments d
LEFT JOIN core.research_objects r
    ON r.department_id = d.department_id
   AND r.deleted_at IS NULL
GROUP BY d.department_id, d.department_name
ORDER BY total_records DESC;

CREATE OR REPLACE VIEW core.v_research_by_output_type AS
SELECT
    ot.output_type_id,
    ot.type_name,
    COUNT(r.research_id) AS total_records
FROM reference.output_types ot
LEFT JOIN core.research_objects r
    ON r.output_type_id = ot.output_type_id
   AND r.deleted_at IS NULL
GROUP BY ot.output_type_id, ot.type_name
ORDER BY total_records DESC;

CREATE OR REPLACE VIEW core.v_metadata_quality_summary AS
SELECT
    CASE
        WHEN metadata_quality_score >= 85 THEN 'high'
        WHEN metadata_quality_score >= 60 THEN 'medium'
        ELSE 'low'
    END AS quality_level,
    COUNT(*) AS total_records
FROM core.research_objects
WHERE deleted_at IS NULL
GROUP BY quality_level;

CREATE OR REPLACE VIEW staging.v_workflow_status_summary AS
SELECT
    workflow_status,
    COUNT(*) AS total_records
FROM staging.research_objects
WHERE deleted_at IS NULL
GROUP BY workflow_status;

-- =============================================================
-- END OF SCHEMA
-- =============================================================


-- =============================================================
"""


DOWNGRADE_STATEMENTS = (
    "DROP SCHEMA IF EXISTS log CASCADE",
    "DROP SCHEMA IF EXISTS core CASCADE",
    "DROP SCHEMA IF EXISTS staging CASCADE",
    "DROP SCHEMA IF EXISTS auth CASCADE",
    "DROP SCHEMA IF EXISTS reference CASCADE",
    "DROP SCHEMA IF EXISTS app CASCADE",
    "DROP EXTENSION IF EXISTS unaccent",
    "DROP EXTENSION IF EXISTS pgcrypto",
)


def _split_sql_statements(sql: str) -> list[str]:
    """Split PostgreSQL SQL text without breaking dollar-quoted function bodies."""
    statements: list[str] = []
    start = 0
    i = 0
    dollar_tag: str | None = None
    in_single_quote = False
    in_double_quote = False
    in_line_comment = False
    in_block_comment = False

    while i < len(sql):
        char = sql[i]
        nxt = sql[i + 1] if i + 1 < len(sql) else ""

        if in_line_comment:
            if char == "\n":
                in_line_comment = False
            i += 1
            continue

        if in_block_comment:
            if char == "*" and nxt == "/":
                in_block_comment = False
                i += 2
            else:
                i += 1
            continue

        if dollar_tag is not None:
            if sql.startswith(dollar_tag, i):
                i += len(dollar_tag)
                dollar_tag = None
            else:
                i += 1
            continue

        if in_single_quote:
            if char == "'":
                if nxt == "'":
                    i += 2
                    continue
                in_single_quote = False
            i += 1
            continue

        if in_double_quote:
            if char == '"':
                in_double_quote = False
            i += 1
            continue

        if char == "-" and nxt == "-":
            in_line_comment = True
            i += 2
            continue

        if char == "/" and nxt == "*":
            in_block_comment = True
            i += 2
            continue

        if char == "'":
            in_single_quote = True
            i += 1
            continue

        if char == '"':
            in_double_quote = True
            i += 1
            continue

        if char == "$":
            j = i + 1
            while j < len(sql) and (sql[j].isalnum() or sql[j] == "_"):
                j += 1
            if j < len(sql) and sql[j] == "$":
                dollar_tag = sql[i : j + 1]
                i = j + 1
                continue

        if char == ";":
            statement = sql[start:i].strip()
            if _has_executable_sql(statement):
                statements.append(statement)
            start = i + 1

        i += 1

    tail = sql[start:].strip()
    if _has_executable_sql(tail):
        statements.append(tail)
    return statements


def _has_executable_sql(statement: str) -> bool:
    return any(line.strip() and not line.strip().startswith("--") for line in statement.splitlines())


def _execute_sql(sql: str) -> None:
    for statement in _split_sql_statements(sql):
        op.execute(statement)


def upgrade() -> None:
    """Create the RDMS database schema."""
    _execute_sql(SCHEMA_SQL)


def downgrade() -> None:
    """Drop the RDMS database schema."""
    for statement in DOWNGRADE_STATEMENTS:
        op.execute(statement)
