import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_TO_FILE: bool = True
    LOG_DIR: str = "logs"
    LOG_ROTATION_BYTES: int = 50 * 1024 * 1024  # 50 MB (50MB per file)
    LOG_RETENTION_COUNT: int = 20  # Keep 20 backup files (~1GB total, ~7-30 days)
    ENVIRONMENT:str = "local"

    class Config:
        env_file = f".env.{os.getenv('ENVIRONMENT', 'dev')}"


settings = Settings()



