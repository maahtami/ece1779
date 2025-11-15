# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str   # required
    secret_key: str = "your-secret-key-change-in-production"  # Change this in production!

    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_DB: str | None = None
    POSTGRES_HOST: str | None = None
    POSTGRES_PORT: str | None = None

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()