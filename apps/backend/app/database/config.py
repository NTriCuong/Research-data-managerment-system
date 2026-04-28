# cấu hình hệ thống dùng chung 
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import toàn bộ entity để Alembic nhận diện
from app.modules.users.models.Role import Role
from app.modules.users.models.User import User
from app.modules.departments.models.Department import Department
from app.modules.authors.models.Author import Author
from app.modules.researches.models.Research import Research
from app.modules.researches.models.Research_Author import ResearchAuthor
from app.modules.researches.models.File import File
from app.modules.researches.models.Keyword import Keyword