from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Intentra"
    APP_ENV: str = "development"
    DATABASE_URL: str
    GEMINI_API_KEY: str
    SECRET_KEY: str = "change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()