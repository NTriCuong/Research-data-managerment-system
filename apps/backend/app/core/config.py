from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",         
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE: int = 30
    REFRESH_TOKEN_EXPIRE: int = 7 

    # Security
    MAX_LOGIN_ATTEMPTS: int = 5 
    LOCK_DURATION: int = 15 


settings = Settings()