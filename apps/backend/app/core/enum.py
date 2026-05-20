import enum


# ============================================================
#  PUBLIC SCHEMA
#  Nguồn: CREATE TYPE user_role AS ENUM ('admin','researcher','viewer')
# ============================================================

class UserRoleEnum(int, enum.Enum):
    """
    Map từ: CREATE TYPE user_role AS ENUM (...)
    public.users.role_id — SMALLINT
    """
    ADMIN      = 1  # ← 'admin'      — Toàn quyền hệ thống
    RESEARCHER = 2  # ← 'researcher' — Tạo/sửa stg_projects
    VIEWER     = 3  # ← 'viewer'     — Chỉ xem (read-only)


# ============================================================
#  STAGING SCHEMA
#  Nguồn: CREATE TYPE stg_project_status AS ENUM (...)
# ============================================================

class StgProjectStatusEnum(int, enum.Enum):
    """
    Map từ: CREATE TYPE stg_project_status AS ENUM (...)
    staging.stg_projects.status — SMALLINT

    Luồng:
      DRAFT → SUBMITTED → UNDER_REVIEW → APPROVED → (copy sang core)
                                       ↘ REJECTED  → (researcher sửa) → SUBMITTED
    """
    DRAFT        = 1  # ← 'draft'        — Researcher đang soạn
    SUBMITTED    = 2  # ← 'submitted'    — Đã nộp, chờ reviewer
    UNDER_REVIEW = 3  # ← 'under_review' — Reviewer đang xem xét
    APPROVED     = 4  # ← 'approved'     — Đã duyệt, sẽ copy sang core
    REJECTED     = 5  # ← 'rejected'     — Bị từ chối, cần sửa lại


class StgDcTypeEnum(int, enum.Enum): #enum cho dublin core type chuẩn 
    """
    Map từ: CREATE TYPE stg_dc_type AS ENUM (...)
    staging.stg_projects.dc_type — SMALLINT
    Loại hình tài liệu theo chuẩn Dublin Core.
    """
    ARTICLE          = 1  # ← 'article'
    THESIS           = 2  # ← 'thesis'
    CONFERENCE_PAPER = 3  # ← 'conference_paper'
    BOOK             = 4  # ← 'book'
    BOOK_CHAPTER     = 5  # ← 'book_chapter'
    REPORT           = 6  # ← 'report'
    DATASET          = 7  # ← 'dataset'
    OTHER            = 8  # ← 'other'


class StgReviewActionEnum(int, enum.Enum):
    """
    Map từ: CREATE TYPE stg_review_action AS ENUM (...)
    staging.stg_reviews.action — SMALLINT
    Hành động của reviewer/approver trên một stg_project.
    """
    APPROVE          = 1  # ← 'approve'          — Phê duyệt → tạo core_project
    REJECT           = 2  # ← 'reject'           — Từ chối hoàn toàn
    REQUEST_REVISION = 3  # ← 'request_revision' — Yêu cầu chỉnh sửa
    COMMENT          = 4  # ← 'comment'          — Góp ý, không đổi status


# ============================================================
#  CORE SCHEMA
#  Nguồn: CREATE TYPE core_project_status AS ENUM (...)
#         CREATE TYPE core_dc_type AS ENUM (...)
#         CREATE TYPE core_citation_relation AS ENUM (...)
# ============================================================

class CoreProjectStatusEnum(int, enum.Enum):
    """
    Map từ: CREATE TYPE core_project_status AS ENUM (...)
    core.core_projects.status — SMALLINT

    Luồng:
      APPROVED → (admin publish) → PUBLISHED
      PUBLISHED → (thu hồi)      → RETRACTED
      PUBLISHED → (ẩn tạm)       → HIDDEN → (mở lại) → PUBLISHED
    """
    APPROVED  = 1  # ← 'approved'  — Đã duyệt, chưa public
    PUBLISHED = 2  # ← 'published' — Công bố, index Elasticsearch
    RETRACTED = 3  # ← 'retracted' — Thu hồi vĩnh viễn
    HIDDEN    = 4  # ← 'hidden'    — Ẩn tạm thời


class CoreDcTypeEnum(int, enum.Enum):
    """
    Map từ: CREATE TYPE core_dc_type AS ENUM (...)
    core.core_projects.dc_type — SMALLINT
    Giống StgDcTypeEnum — tách riêng vì core và staging độc lập.
    """
    ARTICLE          = 1  # ← 'article'
    THESIS           = 2  # ← 'thesis'
    CONFERENCE_PAPER = 3  # ← 'conference_paper'
    BOOK             = 4  # ← 'book'
    BOOK_CHAPTER     = 5  # ← 'book_chapter'
    REPORT           = 6  # ← 'report'
    DATASET          = 7  # ← 'dataset'
    OTHER            = 8  # ← 'other'


class CoreCitationRelationEnum(int, enum.Enum):
    """
    Map từ: CREATE TYPE core_citation_relation AS ENUM (...)
    core.core_citations.relation_type — SMALLINT
    Loại quan hệ trích dẫn giữa 2 nghiên cứu.
    """
    CITES            = 1  # ← 'cites'            — A trích dẫn B
    IS_CITED_BY      = 2  # ← 'is_cited_by'      — A được B trích dẫn
    IS_PART_OF       = 3  # ← 'is_part_of'       — A là một phần của B
    HAS_PART         = 4  # ← 'has_part'         — A chứa B
    REFERENCES       = 5  # ← 'references'       — A tham chiếu B
    IS_REFERENCED_BY = 6  # ← 'is_referenced_by' — A được B tham chiếu


# ============================================================
#  CÁC ENUM BỔ SUNG — không có trong SQL gốc của bạn tôi
#  nhưng cần thiết cho ERD của chúng ta
# ============================================================

class DcLanguageEnum(int, enum.Enum):
    """
    staging.stg_projects.dc_language
    core.core_projects.dc_language — SMALLINT
    Trong SQL gốc lưu VARCHAR(10) ('vi', 'en').
    """
    VI    = 1  # ← 'vi'    — Tiếng Việt
    EN    = 2  # ← 'en'    — Tiếng Anh
    VI_EN = 3  # ← 'vi_en' — Song ngữ


class DcRightsEnum(int, enum.Enum):
    """
    staging.stg_projects.dc_rights
    core.core_projects.dc_rights — SMALLINT
    Trong SQL gốc lưu VARCHAR(255).
    """
    PUBLIC     = 1  # ← 'public'     — Công khai
    RESTRICTED = 2  # ← 'restricted' — Hạn chế nội bộ
    PRIVATE    = 3  # ← 'private'    — Riêng tư


class AuthorTypeEnum(int, enum.Enum):
    """
    public.authors.author_type — SMALLINT
    Phân loại tác giả.
    """
    STUDENT    = 1  # Sinh viên
    LECTURER   = 2  # Giảng viên
    RESEARCHER = 3  # Nhà nghiên cứu


class EducationLevelEnum(int, enum.Enum):
    """
    public.authors.education_level — SMALLINT
    Trình độ học vấn.
    """
    UNDERGRADUATE = 1  # Đại học
    MASTER        = 2  # Thạc sĩ
    DOCTOR        = 3  # Tiến sĩ
    PROFESSOR     = 4  # Giáo sư / Phó giáo sư


class ResearchAuthorRoleEnum(int, enum.Enum):
    """
    staging.stg_research_authors.role
    core.core_research_authors.role — SMALLINT
    Vai trò của tác giả trong một nghiên cứu cụ thể.
    """
    MAIN_AUTHOR  = 1  # Chủ nhiệm đề tài / Tác giả chính
    CO_AUTHOR    = 2  # Đồng tác giả
    SUPERVISOR   = 3  # Giáo viên hướng dẫn
    CONTRIBUTOR  = 4  # Người đóng góp


class KeywordLanguageEnum(int, enum.Enum):
    """
    staging.stg_keywords.language
    core.core_keywords.language — SMALLINT
    """
    VI = 1  # Tiếng Việt
    EN = 2  # Tiếng Anh


class FileTypeEnum(int, enum.Enum):
    """
    staging.stg_files.mime_type category
    core.core_files.mime_type category — SMALLINT
    Phân loại file theo định dạng.
    """
    PDF   = 1
    DOCX  = 2
    XLSX  = 3
    PPTX  = 4
    ZIP   = 5
    OTHER = 6