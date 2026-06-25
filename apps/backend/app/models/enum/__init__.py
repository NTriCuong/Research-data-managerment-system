"""
Enums – RDMS
============
Ánh xạ 1-1 với các PostgreSQL ENUM type được định nghĩa trong schema `app`.

    CREATE TYPE app.user_status     → UserStatus
    CREATE TYPE app.workflow_status → WorkflowStatus
    CREATE TYPE app.access_level    → AccessLevel
    CREATE TYPE app.author_role     → AuthorRole
    CREATE TYPE app.file_status     → FileStatus

Dùng SAEnum trỏ đúng vào PostgreSQL type đã tồn tại (create_type=False)
để tránh Alembic tạo lại type khi autogenerate migration.
"""

import enum

from sqlalchemy import Enum as SAEnum


# ──────────────────────────────────────────────
# app.user_status
# ──────────────────────────────────────────────

class UserStatus(str, enum.Enum):
    """app.user_status — trạng thái tài khoản người dùng."""
    active   = "active"
    disabled = "disabled"


UserStatusType = SAEnum(
    UserStatus,
    name="user_status",
    schema="app",
    create_type=False,  # type đã tồn tại trong DB, không tạo lại
)


# ──────────────────────────────────────────────
# app.workflow_status
# ──────────────────────────────────────────────

class WorkflowStatus(str, enum.Enum):
    """
    app.workflow_status — trạng thái luồng kiểm duyệt.

    draft → pending_review → pending_approval → approved
                           ↘ revision_required
                                               ↘ rejected
    """
    draft              = "draft"
    pending_review     = "pending_review"
    revision_required  = "revision_required"
    pending_approval   = "pending_approval"
    approved           = "approved"
    rejected           = "rejected"


WorkflowStatusType = SAEnum(
    WorkflowStatus,
    name="workflow_status",
    schema="app",
    create_type=False,
)


# ──────────────────────────────────────────────
# app.access_level
# ──────────────────────────────────────────────

class AccessLevel(str, enum.Enum):
    """app.access_level — mức độ truy cập của bản ghi hoặc file."""
    private  = "private"
    internal = "internal"
    public   = "public"


AccessLevelType = SAEnum(
    AccessLevel,
    name="access_level",
    schema="app",
    create_type=False,
)


# ──────────────────────────────────────────────
# app.author_role
# ──────────────────────────────────────────────

class AuthorRole(str, enum.Enum):
    """app.author_role — vai trò của tác giả trong công trình nghiên cứu."""
    creator              = "creator"
    contributor          = "contributor"
    supervisor           = "supervisor"
    student_member       = "student_member"
    corresponding_author = "corresponding_author"


AuthorRoleType = SAEnum(
    AuthorRole,
    name="author_role",
    schema="app",
    create_type=False,
)


# ──────────────────────────────────────────────
# app.file_status
# ──────────────────────────────────────────────

class FileStatus(str, enum.Enum):
    """app.file_status — trạng thái vật lý của file đính kèm."""
    active   = "active"
    replaced = "replaced"
    deleted  = "deleted"


FileStatusType = SAEnum(
    FileStatus,
    name="file_status",
    schema="app",
    create_type=False,
)


# enum notification
class NotificationType(str, enum.Enum):
    PENDING_REVIEW = "PENDING_REVIEW"

    REQUEST_REVISION = "REQUEST_REVISION"

    PENDING_APPROVAL = "PENDING_APPROVAL"

    REJECTED = "REJECTED"

    APPROVAL = "APPROVAL"
