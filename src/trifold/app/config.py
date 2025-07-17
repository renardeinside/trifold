from __future__ import annotations

import logging
from functools import cached_property
from logging import Logger
from pathlib import Path

from databricks.sdk import WorkspaceClient

from dotenv import load_dotenv
from pydantic import BaseModel, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

# Load environment variables from .env file in the root directory of the project
project_root = Path(__file__).parent.parent.parent.parent
env_file = project_root / ".env"

if env_file.exists():
    logger.info(f"Loading environment variables from {env_file}")
    load_dotenv(dotenv_path=env_file)


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file)

    static_assets_path: Path = Field(
        default=Path(__file__).parent / "static",
        description="Path to the static assets directory",
    )


class Runtime(BaseModel):
    conf: AppConfig

    @cached_property
    def logger(self) -> Logger:
        return logger

    @cached_property
    def ws(self) -> WorkspaceClient:
        return WorkspaceClient()

    @model_validator(mode="after")
    def validate_conf(self) -> Runtime:
        self.logger.info(f"Validating conf: {self.conf}")

        try:
            self.ws.current_user.me()
        except Exception as e:
            self.logger.error(
                "Cannot connect to Databricks API using service principal"
            )
            raise e

        return self


conf = AppConfig()
rt = Runtime(conf=conf)
