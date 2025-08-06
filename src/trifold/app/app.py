from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from trifold import __version__
from trifold.app.api import app as api_app
from trifold.app.config import conf, rt
from trifold.app.database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    # Configure global logging to use consistent formatting for all loggers

    rt.logger.info(f"Starting the application with version {__version__}")
    rt.logger.info(f"App config: {conf.model_dump_json(indent=2)}")
    create_db_and_tables()
    yield


app = FastAPI(title="Trifold", lifespan=lifespan)

ui_app = StaticFiles(directory=conf.static_assets_path, html=True)


# note the order of mounts!

app.mount("/api", api_app)
app.mount("/", ui_app)


@app.exception_handler(404)
async def client_side_routing(_, __):
    return FileResponse(conf.static_assets_path / "index.html")
