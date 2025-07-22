from __future__ import annotations

from typing import Any, Callable, Generic, TypeVar
import time

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

T = TypeVar("T")


class TimedCachedProperty(Generic[T]):
    """A property decorator that caches the result for a specified duration."""

    def __init__(self, ttl_seconds: int) -> None:
        self.ttl_seconds = ttl_seconds
        self.cached_value: T | None = None
        self.last_updated: float | None = None
        self.func: Callable[..., T] | None = None

    def __call__(self, func: Callable[..., T]) -> TimedCachedProperty[T]:
        self.func = func
        return self

    def __get__(self, instance: Any, owner: Any = None) -> T:
        if instance is None:
            return self  # type: ignore

        current_time = time.time()

        # Check if we need to refresh the cache
        if (
            self.last_updated is None
            or current_time - self.last_updated > self.ttl_seconds
        ):
            if self.func is not None:
                self.cached_value = self.func(instance)
                self.last_updated = current_time

        return self.cached_value  # type: ignore[return-value]

    def __set_name__(self, owner: Any, name: str) -> None:
        self.name = name

def custom_openapi(app: FastAPI):
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Prefix all paths with /api
    prefixed_paths = {}
    for path in openapi_schema["paths"]:
        prefixed_paths["/api" + path] = openapi_schema["paths"][path]
    openapi_schema["paths"] = prefixed_paths

    app.openapi_schema = openapi_schema
    return app.openapi_schema
