from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "CloudOps Hub"
    environment: str = "local"
    database_url: str = "sqlite:///./cloudops.db"
    redis_url: str = "redis://redis:6379/0"
    jwt_secret: str = "change-this-secret-before-production"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 30
    refresh_token_days: int = 14
    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://localhost:8080"
    aws_region: str = "ap-south-1"

    class Config:
        env_file = ".env"
        env_prefix = "CLOUDOPS_"


@lru_cache
def get_settings() -> Settings:
    return Settings()
