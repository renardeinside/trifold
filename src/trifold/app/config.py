from __future__ import annotations

from functools import cached_property
import logging
from logging import Logger
from pathlib import Path
import uuid

from databricks.sdk import WorkspaceClient

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import Engine
from sqlmodel import Session, create_engine

from trifold.app.utils import TimedCachedProperty, configure_consistent_logging

configure_consistent_logging()

# Get logger for this module - logging will be configured in app startup
logger = logging.getLogger("trifold")
logger.setLevel(logging.DEBUG)

# Load environment variables from .env file in the root directory of the project
project_root = Path(__file__).parent.parent.parent.parent
env_file = project_root / ".env"

if env_file.exists():
    logger.info(f"Loading environment variables from {env_file}")
    load_dotenv(dotenv_path=env_file)


class DatabaseConfig(BaseModel):
    instance_name: str = Field(default="trifold")
    port: int = Field(default=5432)
    database: str = Field(default="databricks_postgres")


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_file, env_prefix="TRIFOLD_", extra="allow"
    )

    static_assets_path: Path = Field(
        default=Path(__file__).parent.parent / "ui" / "dist",
        description="Path to the static assets directory",
    )
    dev_token: SecretStr | None = Field(
        default=None,
        description="Token for local development",
    )

    db: DatabaseConfig = Field(default_factory=DatabaseConfig)


class ConnectionInfo(BaseModel):
    host: str
    port: int
    user: str
    password: str
    database: str

    def to_url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}?sslmode=require"


class Runtime(BaseModel):
    conf: AppConfig

    model_config = ConfigDict(ignored_types=(TimedCachedProperty,))

    @cached_property
    def logger(self) -> Logger:
        return logger

    @cached_property
    def ws(self) -> WorkspaceClient:
        """
        Returns the service principal client.
        """
        return WorkspaceClient()

    def get_connection_info(self) -> ConnectionInfo:
        """
        Returns the SQLAlchemy engine URL used for database operations.
        This URL is initialized with the database URL and can be used to create sessions.
        The URL is cached for 30 minutes to improve performance while ensuring
        credentials are refreshed periodically.
        """
        instance = self.ws.database.get_database_instance(
            name=self.conf.db.instance_name
        )
        cred = self.ws.database.generate_database_credential(
            request_id=str(uuid.uuid4()), instance_names=[self.conf.db.instance_name]
        )
        user = self.ws.current_user.me().user_name
        pwd = cred.token
        host = instance.read_write_dns
        assert host is not None, "Host is not found"
        assert user is not None, "User is not found"
        assert pwd is not None, "Password is not found"

        return ConnectionInfo(
            host=host,
            port=self.conf.db.port,
            user=user,
            password=pwd,
            database=self.conf.db.database,
        )

    @TimedCachedProperty[Engine](ttl_seconds=30 * 60)  # 30 minutes
    def engine(self) -> Engine:
        """
        Returns the SQLAlchemy engine used for database operations.
        This engine is initialized with the database URL and can be used to create sessions.
        The engine is cached for 30 minutes to improve performance while ensuring
        credentials are refreshed periodically.
        """
        self.logger.info("Creating new SQLAlchemy engine (cache expired or first time)")
        return create_engine(
            self.get_connection_info().to_url(),
            # echo=True,
            pool_size=2,
            max_overflow=0,
        )

    @model_validator(mode="after")
    def validate_conf(self) -> Runtime:
        try:
            self.ws.current_user.me()
            assert self.engine is not None, "Engine is not initialized"
        except Exception as e:
            self.logger.error(
                "Cannot connect to Databricks API using service principal"
            )
            raise e

        return self

    def session(self) -> Session:
        """
        Returns the SQLModel session used for database operations.
        This session is initialized with the engine and can be used to create transactions.
        The session is cached for 30 minutes to improve performance while ensuring
        credentials are refreshed periodically.
        """
        return Session(self.engine)


conf = AppConfig()
rt = Runtime(conf=conf)
