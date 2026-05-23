import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from _collections_abc import AsyncGenerator

load_dotenv()


class Base(DeclarativeBase):
    pass


# ── reference (không phụ thuộc schema khác) ──────────────
from app.models.reference.department import Department                              # noqa: E402, F401
from app.models.reference.output_type import OutputType                              # noqa: E402, F401
from app.models.reference.research_domain import ResearchDomain                      # noqa: E402, F401
from app.models.reference.keyword import Keyword                                    # noqa: E402, F401
from app.models.reference.researcher import Researcher                              # noqa: E402, F401

# ── auth (phụ thuộc reference.departments) ────────────────
from app.models.auth.role import Role                                               # noqa: E402, F401
from app.models.auth.user import User                                               # noqa: E402, F401
from app.models.auth.refresh_token import RefreshToken                               # noqa: E402, F401

# ── stagging (phụ thuộc reference + auth) ────────────────
from app.models.stagging.stg_research_object import StgResearchObject                 # noqa: E402, F401
from app.models.stagging.stg_research_object_author import StgResearchObjectAuthor     # noqa: E402, F401
from app.models.stagging.stg_research_object_domain import StgResearchObjectDomain     # noqa: E402, F401
from app.models.stagging.stg_research_object_keyword import StgResearchObjectKeyword   # noqa: E402, F401
from app.models.stagging.stg_file_attachment import StgFileAttachment                 # noqa: E402, F401

# ── core (phụ thuộc stagging + reference + auth) ──────────
from app.models.core.core_research_object import CoreResearchObject                   # noqa: E402, F401
from app.models.core.core_research_object_author import CoreResearchObjectAuthor       # noqa: E402, F401
from app.models.core.core_research_object_domain import CoreResearchObjectDomain       # noqa: E402, F401
from app.models.core.core_research_object_keyword import CoreResearchObjectKeyword     # noqa: E402, F401
from app.models.core.core_file_attachment import CoreFileAttachment                   # noqa: E402, F401
from app.models.core.core_metadata_version import CoreMetadataVersion                 # noqa: E402, F401

# ── logs (phụ thuộc auth + stagging + core) ──────────────
from app.models.logs.workflow_history import WorkflowHistory                         # noqa: E402, F401
from app.models.logs.audit_log import AuditLog                                       # noqa: E402, F401
from app.models.logs.login_log import LoginLog                                       # noqa: E402, F401


DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise