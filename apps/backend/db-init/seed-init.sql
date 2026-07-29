-- =============================================================
-- RDMS SEED DATA
-- Version: 1.0
-- Run after rdms_database_schema.sql
-- =============================================================


BEGIN;


-- =============================================================
-- 1. ROLES
-- =============================================================

INSERT INTO auth.roles
(
    role_code,
    role_name,
    description,
    is_system_role
)
VALUES
(
    'SUPER_ADMIN',
    'Super Administrator',
    'Full system administration permission.',
    TRUE
),
(
    'DATA_ENTRY',
    'Data Entry User',
    'Create and edit research metadata in staging.',
    TRUE
),
(
    'REVIEWER',
    'Metadata Reviewer',
    'Review metadata quality and request revision.',
    TRUE
),
(
    'APPROVER',
    'Metadata Approver',
    'Approve or reject reviewed metadata.',
    TRUE
),
(
    'MANAGER',
    'Research Manager',
    'View dashboards and export reports.',
    TRUE
),
(
    'PUBLIC_USER',
    'Public User',
    'Read-only access to public metadata.',
    TRUE
)
ON CONFLICT(role_code)
DO NOTHING;



-- =============================================================
-- 2. DEPARTMENTS
-- =============================================================

INSERT INTO reference.departments
(
    department_code,
    department_name,
    description
)
VALUES
(
    'FIT',
    'Khoa Công nghệ Thông tin',
    'Faculty of Information Technology'
),
(
    'SCI',
    'Phòng Khoa học Công nghệ',
    'Office of Science and Technology'
),
(
    'QA',
    'Phòng Khảo thí và Đảm bảo chất lượng',
    'Quality Assurance Office'
),
(
    'EDU',
    'Khoa Giáo dục',
    'Faculty of Education'
),
(
    'MATH',
    'Khoa Toán - Tin học',
    'Faculty of Mathematics and Informatics'
)
ON CONFLICT(department_code)
DO NOTHING;



-- =============================================================
-- 3. OUTPUT TYPES
-- =============================================================

INSERT INTO reference.output_types
(
    type_code,
    type_name,
    description
)
VALUES
(
    'RESEARCH_PROJECT',
    'Đề tài nghiên cứu',
    'Research project or institutional research task'
),
(
    'PUBLICATION',
    'Công bố khoa học',
    'Journal paper, conference paper or scholarly publication'
),
(
    'DATASET',
    'Bộ dữ liệu nghiên cứu',
    'Research dataset'
),
(
    'EVIDENCE_DOCUMENT',
    'Tài liệu minh chứng',
    'Evidence document for quality assurance or reporting'
),
(
    'RESEARCH_PRODUCT',
    'Sản phẩm khoa học công nghệ',
    'Software, prototype, model, transfer product'
)
ON CONFLICT(type_code)
DO NOTHING;



-- =============================================================
-- 4. RESEARCH DOMAINS
-- =============================================================

INSERT INTO reference.research_domains
(
    domain_code,
    domain_name,
    description
)
VALUES
(
    'AI',
    'Artificial Intelligence',
    'AI, machine learning, deep learning and intelligent systems'
),
(
    'DS',
    'Data Science',
    'Data analytics, data engineering and data governance'
),
(
    'CYBERSEC',
    'Cyber Security',
    'Information security, network security and zero trust'
),
(
    'IOT',
    'Internet of Things',
    'IoT, edge computing and smart campus'
),
(
    'EDUTECH',
    'Educational Technology',
    'Learning analytics, LMS, digital education'
)
ON CONFLICT(domain_code)
DO NOTHING;



-- =============================================================
-- 5. KEYWORDS
-- =============================================================

INSERT INTO reference.keywords
(
    keyword_text,
    normalized_text
)
VALUES
('metadata','metadata'),
('research data management','research data management'),
('data governance','data governance'),
('FAIR data','fair data'),
('workflow validation','workflow validation'),
('university research','university research'),
('dashboard','dashboard'),
('audit trail','audit trail'),
('semantic search','semantic search'),
('knowledge graph','knowledge graph')
ON CONFLICT(keyword_text)
DO NOTHING;



-- =============================================================
-- 6. RESEARCHERS
-- =============================================================


INSERT INTO reference.researchers
(
    full_name,
    email,
    department_id,
    academic_title,
    researcher_code,
    is_internal
)
SELECT
    'Nguyễn Văn A',
    'nguyenvana@example.edu.vn',
    department_id,
    'TS.',
    'R001',
    TRUE
FROM reference.departments
WHERE department_code='FIT'

ON CONFLICT(email)
DO NOTHING;



INSERT INTO reference.researchers
(
    full_name,
    email,
    department_id,
    academic_title,
    researcher_code,
    is_internal
)
SELECT
    'Trần Thị B',
    'tranthib@example.edu.vn',
    department_id,
    'ThS.',
    'R002',
    TRUE
FROM reference.departments
WHERE department_code='SCI'

ON CONFLICT(email)
DO NOTHING;



INSERT INTO reference.researchers
(
    full_name,
    email,
    department_id,
    academic_title,
    researcher_code,
    is_internal
)
SELECT
    'Lê Văn C',
    'levanc@example.edu.vn',
    department_id,
    'TS.',
    'R003',
    TRUE
FROM reference.departments
WHERE department_code='EDU'

ON CONFLICT(email)
DO NOTHING;



-- =============================================================
-- 7. USERS
-- Password: Admin@12345
-- =============================================================


INSERT INTO auth.users
(
    username,
    email,
    password_hash,
    full_name,
    role_id,
    department_id,
    status
)
SELECT
    'admin',
    'admin@example.edu.vn',
    crypt('Admin@12345', gen_salt('bf')),
    'System Administrator',
    r.role_id,
    d.department_id,
    'active'
FROM auth.roles r,
     reference.departments d
WHERE r.role_code='SUPER_ADMIN'
AND d.department_code='FIT'

ON CONFLICT(username)
WHERE deleted_at IS NULL
DO NOTHING;



INSERT INTO auth.users
(
    username,
    email,
    password_hash,
    full_name,
    role_id,
    department_id,
    status
)
SELECT
    'dataentry01',
    'dataentry01@example.edu.vn',
    crypt('Admin@12345', gen_salt('bf')),
    'Data Entry User 01',
    r.role_id,
    d.department_id,
    'active'
FROM auth.roles r,
reference.departments d
WHERE r.role_code='DATA_ENTRY'
AND d.department_code='SCI'

ON CONFLICT(username)
WHERE deleted_at IS NULL
DO NOTHING;



INSERT INTO auth.users
(
    username,
    email,
    password_hash,
    full_name,
    role_id,
    department_id,
    status
)
SELECT
    'reviewer01',
    'reviewer01@example.edu.vn',
    crypt('Admin@12345', gen_salt('bf')),
    'Metadata Reviewer 01',
    r.role_id,
    d.department_id,
    'active'
FROM auth.roles r,
reference.departments d
WHERE r.role_code='REVIEWER'
AND d.department_code='SCI'

ON CONFLICT(username)
WHERE deleted_at IS NULL
DO NOTHING;



INSERT INTO auth.users
(
    username,
    email,
    password_hash,
    full_name,
    role_id,
    department_id,
    status
)
SELECT
    'approver01',
    'approver01@example.edu.vn',
    crypt('Admin@12345', gen_salt('bf')),
    'Metadata Approver 01',
    r.role_id,
    d.department_id,
    'active'
FROM auth.roles r,
reference.departments d
WHERE r.role_code='APPROVER'
AND d.department_code='SCI'

ON CONFLICT(username)
WHERE deleted_at IS NULL
DO NOTHING;



INSERT INTO auth.users
(
    username,
    email,
    password_hash,
    full_name,
    role_id,
    department_id,
    status
)
SELECT
    'manager01',
    'manager01@example.edu.vn',
    crypt('Admin@12345', gen_salt('bf')),
    'Research Manager 01',
    r.role_id,
    d.department_id,
    'active'
FROM auth.roles r,
reference.departments d
WHERE r.role_code='MANAGER'
AND d.department_code='SCI'

ON CONFLICT(username)
WHERE deleted_at IS NULL
DO NOTHING;



-- =============================================================
-- 8. STAGING RESEARCH OBJECT
-- =============================================================


INSERT INTO staging.research_objects
(
    title,
    description,
    abstract,
    output_type_id,
    department_id,
    year,
    publisher,
    language,
    identifier,
    external_url,
    rights,
    access_level,
    workflow_status,
    created_by
)

SELECT
    'Xây dựng hệ thống quản lý dữ liệu nghiên cứu khoa học dựa trên chuẩn metadata',

    'Đề tài xây dựng RDMS phục vụ chuẩn hóa, kiểm duyệt, tìm kiếm và báo cáo dữ liệu nghiên cứu trong trường đại học.',

    'Research Data Management System using metadata-driven architecture and workflow validation.',

    ot.output_type_id,

    d.department_id,

    2026,

    'HCMUE Demo Repository',

    'vi',

    'RDMS-DEMO-2026-001',

    'https://example.edu.vn/rdms-demo',

    'Internal academic use',

    'internal',

    'draft',

    u.user_id


FROM reference.output_types ot
JOIN reference.departments d
ON d.department_code='FIT'

JOIN auth.users u
ON u.username='dataentry01'

WHERE ot.type_code='RESEARCH_PROJECT'


AND NOT EXISTS
(
    SELECT 1
    FROM staging.research_objects s
    WHERE s.identifier='RDMS-DEMO-2026-001'
);


-- =============================================================
-- 9. AUTHOR
-- =============================================================


INSERT INTO staging.research_object_authors
(
    staging_id,
    researcher_id,
    full_name,
    email,
    affiliation,
    author_order,
    author_role
)

SELECT
    s.staging_id,
    r.researcher_id,
    r.full_name,
    r.email,
    'Khoa Công nghệ Thông tin',
    1,
    'creator'

FROM staging.research_objects s
JOIN reference.researchers r
ON r.email='nguyenvana@example.edu.vn'

WHERE s.identifier='RDMS-DEMO-2026-001'

ON CONFLICT DO NOTHING;



-- =============================================================
-- 10. DOMAIN MAPPING
-- =============================================================


INSERT INTO staging.research_object_domains
(
    staging_id,
    domain_id
)

SELECT
    s.staging_id,
    d.domain_id

FROM staging.research_objects s,
reference.research_domains d

WHERE s.identifier='RDMS-DEMO-2026-001'
AND d.domain_code IN
(
    'DS',
    'EDUTECH'
)

ON CONFLICT DO NOTHING;



-- =============================================================
-- 11. KEYWORD MAPPING
-- =============================================================


INSERT INTO staging.research_object_keywords
(
    staging_id,
    keyword_id
)

SELECT
    s.staging_id,
    k.keyword_id

FROM staging.research_objects s,
reference.keywords k

WHERE s.identifier='RDMS-DEMO-2026-001'
AND k.keyword_text IN
(
'metadata',
'research data management',
'workflow validation',
'audit trail'
)

ON CONFLICT DO NOTHING;



-- =============================================================
-- 12. FILE ATTACHMENT
-- =============================================================


INSERT INTO staging.file_attachments
(
    staging_id,
    original_filename,
    stored_filename,
    storage_path,
    mime_type,
    file_extension,
    file_size_bytes,
    checksum_sha256,
    uploaded_by,
    access_level
)

SELECT
    s.staging_id,

    'rdms_demo_proposal.pdf',

    'rdms_demo_proposal_2026.pdf',

    '/data/rdms/uploads/rdms_demo_proposal_2026.pdf',

    'application/pdf',

    '.pdf',

    102400,

    'demo-checksum-placeholder',

    u.user_id,

    'internal'

FROM staging.research_objects s
JOIN auth.users u
ON u.username='dataentry01'

WHERE s.identifier='RDMS-DEMO-2026-001';



-- =============================================================
-- 13. QUALITY SCORE
-- =============================================================

SELECT app.refresh_staging_metadata_quality(staging_id)
FROM staging.research_objects
WHERE identifier='RDMS-DEMO-2026-001';



COMMIT;