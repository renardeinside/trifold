from __future__ import annotations

import logging
from typing import Any, Callable, Generic, TypeVar
import time

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

T = TypeVar("T")

# Global flag to track if logging has been configured
_logging_configured = False


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


def configure_consistent_logging() -> None:
    """Configure app loggers with consistent formatting"""
    global _logging_configured
    
    # Check if logging has already been configured to avoid duplicates
    if _logging_configured:
        return
    
    # Create the custom formatter with process ID to distinguish workers
    formatter = logging.Formatter(
        fmt="%(asctime)s.%(msecs)03d| %(levelname)-8s | PID:%(process)d | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Create and configure console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)

    # Get the loggers: uvicorn, uvicorn.error, uvicorn.access, trifold and configure them
    for logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access", "trifold", "sqlalchemy.engine", "sqlalchemy.pool", "sqlalchemy.engine"]:
        logger = logging.getLogger(logger_name)
        # Clear existing handlers to avoid duplicates
        logger.handlers.clear()
        logger.addHandler(console_handler)
        # Prevent log propagation to avoid duplicate messages
        logger.propagate = False
    
    # Mark as configured
    _logging_configured = True


def setup_logging(logger_name: str) -> logging.Logger:
    """
    Get a logger with the configured global formatting.

    Args:
        logger_name: Name of the logger to get.

    Returns:
        Logger instance that uses the global configuration.
    """
    return logging.getLogger(logger_name)


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
