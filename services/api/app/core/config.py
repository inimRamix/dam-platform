from typing import Literal

from pydantic import BaseModel
from pydantic.networks import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

LOG_DEFAULT_FORMAT = (
    "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d " "%(levelname)-7s - %(message)s"
)


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    admin: str = "/admin"
    auth: str = "/auth"
    users: str = "/users"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()


class DatabaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 5
    max_overflow: int = 10

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


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
    app_base_url: str = "http://localhost:8000"
    admin_token_expire_minutes: int = 60
    invitation_expire_minutes: int = 120
    # cors_origins: list[str] = ["http://localhost:5173"]


settings = Settings()
