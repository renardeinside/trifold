from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from trifold.app.api import app as api_app
from trifold.app.config import app_conf


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    yield


app = FastAPI(title="Trifold", lifespan=lifespan)

ui_app = StaticFiles(directory=app_conf.static_assets_path, html=True)


# note the order of mounts!

app.mount("/api", api_app)
app.mount("/", ui_app)


@app.exception_handler(404)
async def client_side_routing(_, __):
    return FileResponse(app_conf.static_assets_path / "index.html")
