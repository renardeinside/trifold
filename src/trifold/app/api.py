from functools import partial
from fastapi.responses import JSONResponse
from sqlmodel import select
from databricks.sdk import WorkspaceClient
from fastapi import Depends, FastAPI
from trifold import __version__
from trifold.app.config import rt
from trifold.app.dependencies import get_user_workspace_client
from trifold.app.models import (
    Dessert,
    DessertIn,
    DessertOut,
    ProfileView,
    VersionView,
    get_cached_version,
)
from trifold.app.utils import custom_openapi

app = FastAPI(
    title="Trifold | Full stack data application on Databricks",
    description="Trifold is a full stack data application on Databricks",
    version=__version__,
)


@app.get("/version", response_model=VersionView, operation_id="Version")
async def version():
    return get_cached_version()


@app.get("/profile", response_model=ProfileView, operation_id="Profile")
async def profile(ws: WorkspaceClient = Depends(get_user_workspace_client)):
    return ProfileView.from_ws(ws)


@app.get("/desserts", response_model=list[DessertOut], operation_id="Desserts")
async def desserts():
    with rt.session as session:
        return [DessertOut.from_model(d) for d in session.exec(select(Dessert)).all()]


@app.post("/desserts", response_model=DessertOut, operation_id="CreateDessert")
async def create_dessert(dessert: DessertIn):
    with rt.session as session:
        model = Dessert(**dessert.model_dump())
        session.add(model)
        session.commit()
        return DessertOut.from_model(model)


@app.put(
    "/desserts/{dessert_id}", response_model=DessertOut, operation_id="UpdateDessert"
)
async def update_dessert(dessert_id: int, dessert: DessertIn):
    with rt.session as session:
        model = session.get(Dessert, dessert_id)
        if not model:
            return JSONResponse(
                status_code=404, content={"detail": "Dessert not found"}
            )
        model.name = dessert.name
        model.price = dessert.price
        model.description = dessert.description
        model.left_in_stock = dessert.left_in_stock
        session.commit()
        return DessertOut.from_model(model)


@app.delete("/desserts/{dessert_id}", response_model=None, operation_id="DeleteDessert")
async def delete_dessert(dessert_id: int):
    with rt.session as session:
        model = session.get(Dessert, dessert_id)
        if not model:
            return JSONResponse(
                status_code=404, content={"detail": "Dessert not found"}
            )
        session.delete(model)
        session.commit()
        return JSONResponse(status_code=204, content={"detail": "Dessert deleted"})


app.openapi = partial(custom_openapi, app)
