import enum

class UserRoleEnum(int, enum.Enum):
    ADMIN      = 1  
    RESEARCHER = 2  
    VIEWER     = 3  


class StgProjectStatusEnum(int, enum.Enum):
    DRAFT        = 1 
    SUBMITTED    = 2 
    UNDER_REVIEW = 3 
    APPROVED     = 4  
    REJECTED     = 5  


class StgDcTypeEnum(int, enum.Enum): 
    ARTICLE          = 1  
    THESIS           = 2 
    CONFERENCE_PAPER = 3  
    BOOK             = 4 
    BOOK_CHAPTER     = 5 
    REPORT           = 6  
    DATASET          = 7  
    OTHER            = 8  


class StgReviewActionEnum(int, enum.Enum):
    APPROVE          = 1  
    REJECT           = 2 
    REQUEST_REVISION = 3  
    COMMENT          = 4  


class CoreProjectStatusEnum(int, enum.Enum):
    APPROVED  = 1 
    PUBLISHED = 2  
    RETRACTED = 3  # Thu hồi vĩnh viễn
    HIDDEN    = 4  


class CoreDcTypeEnum(int, enum.Enum):
    ARTICLE          = 1  
    THESIS           = 2  
    CONFERENCE_PAPER = 3
    BOOK             = 4  
    BOOK_CHAPTER     = 5  
    REPORT           = 6 
    DATASET          = 7  
    OTHER            = 8  


class CoreCitationRelationEnum(int, enum.Enum):
    CITES            = 1  # ← 'cites'            — A trích dẫn B
    IS_CITED_BY      = 2  # ← 'is_cited_by'      — A được B trích dẫn
    IS_PART_OF       = 3  # ← 'is_part_of'       — A là một phần của B
    HAS_PART         = 4  # ← 'has_part'         — A chứa B
    REFERENCES       = 5  # ← 'references'       — A tham chiếu B
    IS_REFERENCED_BY = 6  # ← 'is_referenced_by' — A được B tham chiếu



class DcLanguageEnum(int, enum.Enum):
    VI    = 1 
    EN    = 2  
    VI_EN = 3  


class DcRightsEnum(int, enum.Enum):
    PUBLIC     = 1  
    RESTRICTED = 2  
    PRIVATE    = 3  


class AuthorTypeEnum(int, enum.Enum):
    STUDENT    = 1  # Sinh viên
    LECTURER   = 2  # Giảng viên
    RESEARCHER = 3  # Nhà nghiên cứu


class EducationLevelEnum(int, enum.Enum):
    UNDERGRADUATE = 1  # Đại học
    MASTER        = 2  # Thạc sĩ
    DOCTOR        = 3  # Tiến sĩ
    PROFESSOR     = 4  # Giáo sư / Phó giáo sư


class ResearchAuthorRoleEnum(int, enum.Enum):
    MAIN_AUTHOR  = 1 
    CO_AUTHOR    = 2  # Đồng tác giả
    SUPERVISOR   = 3  
    CONTRIBUTOR  = 4  


class KeywordLanguageEnum(int, enum.Enum):
    VI = 1 
    EN = 2  


class FileTypeEnum(int, enum.Enum):
    PDF   = 1
    DOCX  = 2
    XLSX  = 3
    PPTX  = 4
    ZIP   = 5
    OTHER = 6