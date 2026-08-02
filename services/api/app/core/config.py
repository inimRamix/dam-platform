from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field
from pydantic.networks import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

LOG_DEFAULT_FORMAT = (
    "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d " "%(levelname)-7s - %(message)s"
)


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()


class DatabaseConfig(BaseModel):
    url: PostgresDsn = Field(alias="DATABASE_URL")
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 5
    max_overflow: int = 10


class JwtConfig(BaseModel):
    secret_key: str = Field(alias="JWT_SECRET_KEY")
    algorithm: str = Field(alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = 30


class SmtpConfig(BaseModel):
    host: str = Field(default="mailhog", alias="SMTP_HOST")
    port: int = Field(default=1025, alias="SMTP_PORT")
    username: str = Field(alias="SMTP_USERNAME")
    password: str = Field(alias="SMTP_PASSWORD")
    from_email: str = Field(alias="SMTP_FROM")


class LoggingConfig(BaseModel):
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    format: str = LOG_DEFAULT_FORMAT


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        populate_by_name=True,
    )
    api: ApiPrefix = ApiPrefix()
    db: DatabaseConfig
    jwt: JwtConfig
    smtp: SmtpConfig = SmtpConfig()
    logging: LoggingConfig = LoggingConfig()
    deploy_mode: str = Field(default="production", alias="DEPLOY_MODE")


settings = Settings()
