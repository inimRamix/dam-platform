from typing import Literal

from pydantic import BaseModel
from pydantic.networks import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

LOG_DEFAULT_FORMAT = (
    "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d " "%(levelname)-7s - %(message)s"
)


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()


class DatabaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 5
    max_overflow: int = 10


class JwtConfig(BaseModel):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int = 30


class SmtpConfig(BaseModel):
    host: str
    port: int
    username: str
    password: str
    from_email: str


class LoggingConfig(BaseModel):
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    format: str = LOG_DEFAULT_FORMAT


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    api: ApiPrefix = ApiPrefix()
    db: DatabaseConfig
    jwt: JwtConfig
    smtp: SmtpConfig
    logging: LoggingConfig = LoggingConfig()
    deploy_mode: str = "production"


settings = Settings()
