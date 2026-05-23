from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    SECRET_KEY: str
    ALGORITHM: str 
    ACCESS_TOKEN_EXPIRE: int 
    REFRESH_TOKEN_EXPIRE: int 

    MAX_LOGIN_ATTEMPTS: int 
    LOCK_DURATION: int 


settings = Settings()
