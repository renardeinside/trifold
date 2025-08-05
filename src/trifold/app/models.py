from __future__ import annotations

from functools import lru_cache

from databricks.sdk import WorkspaceClient
from databricks.sdk.service import iam
from trifold import __version__
from sqlalchemy import DDL, event

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
    id: int | None = SQLField(primary_key=True, default=None)
    name: str
    price: float
    description: str
    left_in_stock: int = SQLField(default=0)

    @classmethod
    def from_in(cls, in_: DessertIn) -> Dessert:
        return cls(
            name=in_.name,
            price=in_.price,
            description=in_.description,
            left_in_stock=in_.left_in_stock,
        )

    def update_from_in(self, in_: DessertIn) -> None:
        self.name = in_.name
        self.price = in_.price
        self.description = in_.description
        self.left_in_stock = in_.left_in_stock


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
