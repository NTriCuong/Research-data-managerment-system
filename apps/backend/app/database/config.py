import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()


# ============================================================
#  Base
#  Tất cả model kế thừa class này.
#  Alembic đọc Base.metadata để sinh migration tự động.
# ============================================================

class Base(DeclarativeBase):
    pass


# ============================================================
#  Import toàn bộ model — BẮT BUỘC
#
#  SQLAlchemy chỉ đăng ký table vào metadata khi module của
#  nó được import. Thiếu 1 dòng → Alembic bỏ sót table đó
#  → không sinh migration cho table đó.
#
#  Cấu trúc thư mục:
#  app/modules/
#    ├── system/models/    → public schema
#    │     Role, Department, User, Refresh_token, Author
#    ├── stagging/models/  → staging schema
#    │     Stg_Project, Stg_File, Stg_Research_Author,
#    │     Stg_keyword, Stg_review, Stg_Field_Comment
#    ├── core/models/      → core schema
#    │     Core_Project, Core_Models
#    └── logs/models/      → log schema
#           logs (AuditLog + LoginLog)
#
#  Thứ tự import:
#    system → stagging → core → logs
#  (bảng cha trước bảng con có FK trỏ vào)
# ============================================================

# ── SYSTEM — public schema ───────────────────────────────────
from app.modules.system.models.Role import Role                                     # noqa: E402
from app.modules.system.models.Department import Department                         # noqa: E402
from app.modules.system.models.User import User                                     # noqa: E402
from app.modules.system.models.Refresh_token import RefreshToken                    # noqa: E402
from app.modules.system.models.Author import Author                                 # noqa: E402

# ── STAGGING — staging schema ────────────────────────────────
from app.modules.stagging.models.Stg_Project import StgProject                      # noqa: E402
from app.modules.stagging.models.Stg_File import StgFile                            # noqa: E402
from app.modules.stagging.models.Stg_Research_Author import StgResearchAuthor       # noqa: E402
from app.modules.stagging.models.Stg_keyword import StgKeyword                      # noqa: E402
from app.modules.stagging.models.Stg_review import StgReview                        # noqa: E402
from app.modules.stagging.models.Stg_Field_Comment import StgFieldComment           # noqa: E402

# ── CORE — core schema ───────────────────────────────────────
from app.modules.core.models.Core_Project import CoreProject                        # noqa: E402
from app.modules.core.models.Core_Models import (                                   # noqa: E402
    CoreFile,
    CoreResearchAuthor,
    CoreKeyword,
    CoreEditLog,
    CoreCitation,
)

# ── LOGS — log schema ────────────────────────────────────────
from app.modules.logs.models.logs import AuditLog, LoginLog                         # noqa: E402


# ============================================================
#  Async Engine
#
#  DATABASE_URL đọc từ .env:
#  DATABASE_URL=postgresql+asyncpg://postgres:Ntc%401504@localhost:5432/rdms
#
#  asyncpg   : driver async bắt buộc, không dùng psycopg2
#  echo=True : in SQL ra console khi debug
#              → đổi thành False khi production
#  future=True: bắt buộc cho SQLAlchemy 2.x API
# ============================================================

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
)


# ============================================================
#  Session Factory
#
#  expire_on_commit=False:
#    Sau khi commit, object vẫn giữ nguyên attribute.
#    Nếu để True → SQLAlchemy expire object → lần đọc tiếp
#    theo sẽ lazy-load lại → lỗi trong async context vì
#    không thể implicit I/O.
# ============================================================

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ============================================================
#  get_db — Dependency Injection cho FastAPI
#
#  Cách dùng trong router:
#    from app.database.config import get_db
#
#    @router.get("/projects")
#    async def get_projects(db: AsyncSession = Depends(get_db)):
#        result = await db.execute(select(StgProject))
#        return result.scalars().all()
#
#  Lifecycle mỗi request:
#    1. Mở session mới
#    2. yield session cho handler dùng
#    3. Thành công → commit
#    4. Exception  → rollback
#    5. Finally    → đóng session (async with tự xử lý)
# ============================================================

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise