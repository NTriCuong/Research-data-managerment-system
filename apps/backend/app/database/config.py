import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()


class Base(DeclarativeBase):
    pass


# ── reference (không phụ thuộc schema khác) ──────────────
from app.models.reference.Department import Department                              # noqa: E402, F401
from app.models.reference.Outputtype import OutputType                              # noqa: E402, F401
from app.models.reference.Researchdomain import ResearchDomain                      # noqa: E402, F401
from app.models.reference.Keyword import Keyword                                    # noqa: E402, F401
from app.models.reference.Researcher import Researcher                              # noqa: E402, F401

# ── auth (phụ thuộc reference.departments) ────────────────
from app.models.auth.Role import Role                                               # noqa: E402, F401
from app.models.auth.user import User                                               # noqa: E402, F401
from app.models.auth.RefreshToken import RefreshToken                               # noqa: E402, F401

# ── stagging (phụ thuộc reference + auth) ────────────────
from app.models.stagging.Stgresearchobject import StgResearchObject                 # noqa: E402, F401
from app.models.stagging.Stgresearchobjectauthor import StgResearchObjectAuthor     # noqa: E402, F401
from app.models.stagging.Stgresearchobjectdomain import StgResearchObjectDomain     # noqa: E402, F401
from app.models.stagging.Stgresearchobjectkeyword import StgResearchObjectKeyword   # noqa: E402, F401
from app.models.stagging.Stgfileattachment import StgFileAttachment                 # noqa: E402, F401

# ── core (phụ thuộc stagging + reference + auth) ──────────
from app.models.core.Coreresearchobject import CoreResearchObject                   # noqa: E402, F401
from app.models.core.Coreresearchobjectauthor import CoreResearchObjectAuthor       # noqa: E402, F401
from app.models.core.Coreresearchobjectdomain import CoreResearchObjectDomain       # noqa: E402, F401
from app.models.core.Coreresearchobjectkeyword import CoreResearchObjectKeyword     # noqa: E402, F401
from app.models.core.Corefileattachment import CoreFileAttachment                   # noqa: E402, F401
from app.models.core.Coremetadataversion import CoreMetadataVersion                 # noqa: E402, F401

# ── logs (phụ thuộc auth + stagging + core) ──────────────
from app.models.logs.Workflowhistory import WorkflowHistory                         # noqa: E402, F401
from app.models.logs.Auditlog import AuditLog                                       # noqa: E402, F401
from app.models.logs.Loginlog import LoginLog                                       # noqa: E402, F401


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


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise