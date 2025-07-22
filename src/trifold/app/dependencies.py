import os

from databricks.sdk import WorkspaceClient
from fastapi import Request

from trifold.app.config import rt,conf


def get_user_workspace_client(
    request: Request,
) -> WorkspaceClient:
    """
    Returns a Databricks Workspace client with authentication behalf of user.
    If the request contains an X-Forwarded-Access-Token header, on behalf of user authentication is used.
    Otherwise, the client is created using the default environemnt variables (e.g. during local development)
    """
    token = request.headers.get("X-Forwarded-Access-Token") or conf.dev_token.get_secret_value() if conf.dev_token else None
    if not token:
        raise ValueError(
            "No token for authentication provided in request headers or environment variables"
        )

    rt.logger.info("Received OBO token, initializing client with it")
    return WorkspaceClient(
        token=token,
    )  # set pat explicitly to avoid issues with SP client
