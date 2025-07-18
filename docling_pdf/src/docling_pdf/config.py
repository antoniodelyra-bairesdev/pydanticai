from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "PDF to Markdown API"
    app_version: str = "1.0.0"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    # Upload settings
    max_file_size: int = 50 * 1024 * 1024
    upload_timeout: int = 300
    temp_dir: str = "uploads/temp"
    allowed_extensions: list[str] = Field(default_factory=lambda: ["pdf"])

    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    class Config:
        env_file = None
        env_file_encoding = "utf-8"


settings = Settings()
