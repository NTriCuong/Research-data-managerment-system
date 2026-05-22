import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

#  Tất cả model kế thừa class này.

class Base(DeclarativeBase):
    pass

from app.models.system.Role import Role                                     
from app.models.system.Department import Department                         
from app.models.system.User import User                                     
from app.models.system.Refresh_token import RefreshToken                    
from app.models.system.Author import Author                                 

from app.models.stagging.Stg_Project import StgProject                      
from app.models.stagging.Stg_File import StgFile                            
from app.models.stagging.Stg_Research_Author import StgResearchAuthor       
from app.models.stagging.Stg_keyword import StgKeyword                      
from app.models.stagging.Stg_review import StgReview                        
from app.models.stagging.Stg_Field_Comment import StgFieldComment           

from app.models.core.Core_Project import CoreProject                        
from app.models.core.Core_Models import (                                   
    CoreFile,
    CoreResearchAuthor,
    CoreKeyword,
    CoreEditLog,
    CoreCitation,
)

from app.models.logs.logs import AuditLog, LoginLog                         

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