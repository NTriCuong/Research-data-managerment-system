import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

#  Base
#  Tất cả model kế thừa class này.

class Base(DeclarativeBase):
    pass

from app.modules.system.models.Role import Role                                     
from app.modules.system.models.Department import Department                         
from app.modules.system.models.User import User                                     
from app.modules.system.models.Refresh_token import RefreshToken                    
from app.modules.system.models.Author import Author                                 

from app.modules.stagging.models.Stg_Project import StgProject                      
from app.modules.stagging.models.Stg_File import StgFile                            
from app.modules.stagging.models.Stg_Research_Author import StgResearchAuthor       
from app.modules.stagging.models.Stg_keyword import StgKeyword                      
from app.modules.stagging.models.Stg_review import StgReview                        
from app.modules.stagging.models.Stg_Field_Comment import StgFieldComment           

from app.modules.core.models.Core_Project import CoreProject                        
from app.modules.core.models.Core_Models import (                                   
    CoreFile,
    CoreResearchAuthor,
    CoreKeyword,
    CoreEditLog,
    CoreCitation,
)

from app.modules.logs.models.logs import AuditLog, LoginLog                         

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