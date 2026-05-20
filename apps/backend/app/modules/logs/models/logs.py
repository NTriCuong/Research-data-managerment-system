import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base


# ============================================================
#  AuditLog  — theo thiết kế bạn tôi
# ============================================================

class AuditLog(Base):
    """
    Audit log chung toàn hệ thống.

    Ghi lại MỌI thay đổi dữ liệu quan trọng:
    CREATE, UPDATE, DELETE, APPROVE, REJECT, PUBLISH, REVOKE...

    Cách dùng trong service layer:
        db.add(AuditLog(
            user_id     = current_user.id,
            action      = "APPROVE",
            entity_type = "stg_project",
            entity_id   = project.id,
            old_value   = {"status": 3},
            new_value   = {"status": 4},
            ip_address  = request.client.host,
        ))

    Khác với login_logs (chỉ track login/logout),
    audit_logs track TẤT CẢ hành động trên data.
    """
    __tablename__ = "audit_logs"
    __table_args__ = (
        # Composite index: query "toàn bộ log của research X"
        # WHERE entity_type='stg_project' AND entity_id='xxx' → rất nhanh
        Index("idx_audit_entity",     "entity_type", "entity_id"),
        Index("idx_audit_user",       "user_id"),
        Index("idx_audit_created_at", "created_at"),
        {"schema": "log"},
    )

    # PK | id          | VARCHAR(36)
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # FK | user_id     | VARCHAR(36) → public.users.id
    # SET NULL: user bị xóa thì audit log vẫn còn, user_id = NULL
    user_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("public.users.id", ondelete="SET NULL"), nullable=True
    )

    # N  | action      | VARCHAR(50)
    # Dùng VARCHAR thay ENUM số → linh hoạt, không cần migration khi thêm action
    # Convention: 'CREATE' 'UPDATE' 'DELETE' 'LOGIN' 'LOGOUT'
    #             'APPROVE' 'REJECT' 'PUBLISH' 'REVOKE' 'SUBMIT'
    action: Mapped[str] = mapped_column(String(50), nullable=False)

    # N  | entity_type | VARCHAR(50) — loại object bị tác động
    # Convention: 'user' 'stg_project' 'core_project' 'stg_file' 'author'
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # N  | entity_id   | VARCHAR(36) — ID của object cụ thể
    entity_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    # N  | old_value   | JSONB — data TRƯỚC thay đổi (NULL nếu CREATE)
    old_value: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # N  | new_value   | JSONB — data SAU thay đổi (NULL nếu DELETE)
    new_value: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # N  | ip_address  | INET — PostgreSQL tự validate IPv4/IPv6
    ip_address: Mapped[Optional[str]] = mapped_column(INET, nullable=True)

    # N  | created_at  | TIMESTAMPTZ
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    user = relationship("User", back_populates="audit_logs")


# ============================================================
#  LoginLog  — tách riêng để phân tích security
# ============================================================

class LoginLog(Base):
    """
    Track mọi attempt login — thành công lẫn thất bại.

    Dùng để:
    - Phát hiện brute-force attack (nhiều failure từ 1 IP)
    - Phát hiện credential stuffing (1 user bị thử từ nhiều IP)
    - Audit security: ai login từ đâu, khi nào
    """
    __tablename__ = "login_logs"
    __table_args__ = (
        Index("idx_login_user",       "user_id"),
        Index("idx_login_created_at", "created_at"),
        {"schema": "log"},
    )

    # PK | id              | VARCHAR(36)
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # FK | user_id         | VARCHAR(36) → public.users.id
    # NULL: login sai email hoàn toàn → không tìm được user nào khớp
    user_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("public.users.id", ondelete="SET NULL"), nullable=True
    )

    # N  | email_attempted | VARCHAR(320) — email được nhập (đúng hay sai đều ghi)
    email_attempted: Mapped[str] = mapped_column(String(320), nullable=False)

    # N  | success         | BOOLEAN
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # N  | failure_reason  | VARCHAR(100) — NULL nếu success=True
    # VD: 'wrong_password' 'account_locked' 'account_inactive' 'account_deleted'
    failure_reason: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # N  | ip_address      | INET
    ip_address: Mapped[Optional[str]] = mapped_column(INET, nullable=True)

    # N  | user_agent      | TEXT — browser/device info
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # N  | created_at      | TIMESTAMPTZ
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    user = relationship("User", back_populates="login_logs")