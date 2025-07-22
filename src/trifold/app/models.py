from __future__ import annotations

from functools import lru_cache

from databricks.sdk import WorkspaceClient
from databricks.sdk.service import iam
from trifold import __version__

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from sqlmodel import SQLModel, Field as SQLField


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel, serialize_by_alias=True, populate_by_name=True
    )


class VersionView(CamelModel):
    """
    Model representing the version information of the package.
    """

    version: str


@lru_cache(maxsize=1)
def get_cached_version() -> VersionView:
    """Cache the version information since it doesn't change during runtime."""
    return VersionView(version=__version__)


class ProfileView(CamelModel):
    user: iam.User

    @classmethod
    def from_ws(cls, ws: WorkspaceClient) -> "ProfileView":
        return cls(user=ws.current_user.me())


class DessertIn(CamelModel):
    name: str
    price: float
    description: str
    left_in_stock: int


class Dessert(SQLModel, table=True):
    id: int | None = SQLField(primary_key=True)
    name: str
    price: float
    description: str
    left_in_stock: int = SQLField(default=0)


class DessertOut(CamelModel):
    id: int
    name: str
    price: float
    description: str
    left_in_stock: int

    @classmethod
    def from_model(cls, model: Dessert) -> DessertOut:
        assert model.id is not None, f"Dessert {model.name} has no id"
        return cls(
            id=model.id,
            name=model.name,
            price=model.price,
            description=model.description,
            left_in_stock=model.left_in_stock,
        )
