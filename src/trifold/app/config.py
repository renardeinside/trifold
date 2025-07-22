from __future__ import annotations

import logging
from functools import cached_property
from logging import Logger
from pathlib import Path
import uuid

from databricks.sdk import WorkspaceClient

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import Engine
from sqlmodel import Session, create_engine

from trifold.app.utils import TimedCachedProperty

# Configure logger with nice formatting
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create formatter with function name
formatter = logging.Formatter(
    fmt='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Create console handler and set formatter
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Clear any existing handlers and add our custom handler
logger.handlers.clear()
logger.addHandler(console_handler)

# Prevent propagation to avoid duplicate messages
logger.propagate = False

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

    @TimedCachedProperty[Engine](ttl_seconds=30 * 60)  # 30 minutes
    def engine(self) -> Engine:
        """
        Returns the SQLAlchemy engine used for database operations.
        This engine is initialized with the database URL and can be used to create sessions.
        The engine is cached for 30 minutes to improve performance while ensuring
        credentials are refreshed periodically.
        """
        self.logger.info("Creating new SQLAlchemy engine (cache expired or first time)")
        instance = self.ws.database.get_database_instance(
            name=self.conf.db.instance_name
        )
        cred = self.ws.database.generate_database_credential(
            request_id=str(uuid.uuid4()), instance_names=[self.conf.db.instance_name]
        )
        user = self.ws.current_user.me().user_name
        pwd = cred.token
        host = instance.read_write_dns
        url = f"postgresql://{user}:{pwd}@{host}:{self.conf.db.port}/{self.conf.db.database}?sslmode=require"
        return create_engine(
            url,
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

    @TimedCachedProperty[Session](ttl_seconds=30 * 60)  # 30 minutes
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
