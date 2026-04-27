
-- ROLES
CREATE TABLE roles (
    id INTEGER PRIMARY KEY,
    name VARCHAR(20) UNIQUE NOT NULL
);

-- DEPARTMENTS
CREATE TABLE departments (
    id SMALLINT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

-- USERS
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(50) NOT NULL,
    user_code VARCHAR(15) UNIQUE NOT NULL,
    role_id INTEGER NOT NULL,
    create_at DATE NOT NULL,
    update_at DATE NOT NULL,
    status SMALLINT NOT NULL,

    CONSTRAINT fk_users_role
        FOREIGN KEY (role_id) REFERENCES roles(id)
);

-- AUTHORS
CREATE TABLE authors (
    id INTEGER PRIMARY KEY,
    full_name VARCHAR(50) NOT NULL,
    email VARCHAR(50) UNIQUE NOT NULL,
    author_code VARCHAR(12) NOT NULL,
    author_type SMALLINT NOT NULL,
    education_level SMALLINT NOT NULL,
    department_id SMALLINT NOT NULL,

    CONSTRAINT uq_authors_author_code UNIQUE (author_code),

    CONSTRAINT fk_authors_department
        FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- RESEARCHES
CREATE TABLE researches (
    id INTEGER PRIMARY KEY,
    research_code VARCHAR(36) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    abstract TEXT NOT NULL,
    publication_date DATE NOT NULL,
    status SMALLINT NOT NULL,
    created_at DATE NOT NULL,
    version VARCHAR(3) NOT NULL,
    department_id SMALLINT NOT NULL,
    metadata TEXT NOT NULL,

    CONSTRAINT fk_researches_department
        FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- KEYWORDS
CREATE TABLE keywords (
    id INTEGER PRIMARY KEY,
    key TEXT NOT NULL,
    research_code VARCHAR(36) NOT NULL,

    CONSTRAINT fk_keywords_researches
        FOREIGN KEY (research_code) REFERENCES researches(research_code)
);

-- FILES
CREATE TABLE files (
    id INTEGER PRIMARY KEY,
    research_code VARCHAR(36) NOT NULL,
    file_name VARCHAR(20) NOT NULL,
    file_type SMALLINT NOT NULL,
    file_size FLOAT NOT NULL,
    upload_by VARCHAR(36) NOT NULL,
    file_url TEXT NOT NULL,

    CONSTRAINT fk_files_researches
        FOREIGN KEY (research_code) REFERENCES researches(research_code),

    CONSTRAINT fk_files_users
        FOREIGN KEY (upload_by) REFERENCES users(id)
);

-- RESEARCH_AUTHOR
CREATE TABLE research_author (
    id INTEGER PRIMARY KEY,
    research_code VARCHAR(36) NOT NULL,
    author_id INTEGER NOT NULL,
    role SMALLINT NOT NULL,

    CONSTRAINT fk_research_author_researches
        FOREIGN KEY (research_code) REFERENCES researches(research_code),

    CONSTRAINT fk_research_author_authors
        FOREIGN KEY (author_id) REFERENCES authors(id)
);

-- ACTIVITY_LOG
CREATE TABLE activity_log (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    action TEXT NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    create_at TIMESTAMP NOT NULL,

    CONSTRAINT fk_activity_log_users
        FOREIGN KEY (user_id) REFERENCES users(id)
);

-- index tối ưu search cho sql query
-- EXTENSION
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Giữ dạng expression index (không cần thêm column)
CREATE INDEX idx_researches_fts
ON researches
USING GIN (
    to_tsvector('simple', coalesce(title,'') || ' ' || coalesce(abstract,''))
);

-- 2. SEARCH NAME (gõ gần đúng)
CREATE INDEX idx_researches_title_trgm
ON researches
USING GIN (title gin_trgm_ops);

CREATE INDEX idx_authors_name_trgm
ON authors
USING GIN (full_name gin_trgm_ops);

CREATE INDEX idx_keywords_key_trgm
ON keywords
USING GIN (key gin_trgm_ops);

-- 3. FILTER (date + department)
CREATE INDEX idx_researches_pub_date
ON researches(publication_date);

CREATE INDEX idx_researches_department
ON researches(department_id);

-- 4. JOIN TỐI ƯU (QUAN TRỌNG NHẤT)
-- bảng trung gian (author <-> research)
DROP INDEX IF EXISTS idx_ra_author;
DROP INDEX IF EXISTS idx_ra_research;

CREATE INDEX idx_ra_author_research
ON research_author(author_id, research_code);

CREATE INDEX idx_ra_research_author
ON research_author(research_code, author_id);

-- keyword join
DROP INDEX IF EXISTS idx_keywords_research;

CREATE INDEX idx_keywords_research_key
ON keywords(research_code, key);

--  5. LOG SEARCH (ADMIN)
-- chỉ giữ composite index (tốt hơn 2 index đơn)
DROP INDEX IF EXISTS idx_log_user;
DROP INDEX IF EXISTS idx_log_date;

CREATE INDEX idx_log_user_date
ON activity_log(user_id, create_at);