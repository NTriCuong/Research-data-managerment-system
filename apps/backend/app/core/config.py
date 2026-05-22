from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",          # cùng file .env 
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE: int = 30
    REFRESH_TOKEN_EXPIRE: int = 7 #fallback nếu không có trong .env

    # Security
    MAX_LOGIN_ATTEMPTS: int = 5 # số lần đăng nhập sai tối đa trước khi bị khoá tài khoản
    LOCK_DURATION: int = 15 # thời gian khoá tài khoản (phút)


settings = Settings()