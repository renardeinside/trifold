import asyncio
from functools import partial
from typing import AsyncGenerator
import asyncpg
from fastapi.responses import StreamingResponse
from sqlmodel import select
from fastapi import FastAPI, HTTPException, Request
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
from trifold.app.notify import NOTIFY_CHANNEL, Notification, NotificationOut


app = FastAPI(
    title="Trifold | Full stack data application on Databricks",
    description="Trifold is a full stack data application on Databricks",
    version=__version__,
)


@app.get("/version", response_model=VersionView, operation_id="Version")
async def version():
    return get_cached_version()


@app.get("/profile", response_model=ProfileView, operation_id="Profile")
async def profile(request: Request):
    try:
        ws = get_user_workspace_client(request)
        return ProfileView.from_ws(ws)
    except Exception as e:
        rt.logger.error(f"Error getting user workspace client: {e}")
        return ProfileView.from_request(request)


@app.get("/desserts", response_model=list[DessertOut], operation_id="Desserts")
async def desserts() -> list[DessertOut]:
    with rt.session() as session:
        return [DessertOut.from_model(d) for d in session.exec(select(Dessert)).all()]


@app.post("/desserts", response_model=DessertOut, operation_id="CreateDessert")
async def create_dessert(dessert: DessertIn):
    with rt.session() as session:
        model = Dessert.from_in(dessert)
        session.add(model)
        session.commit()
        return DessertOut.from_model(model)


@app.put(
    "/desserts/{dessert_id}", response_model=DessertOut, operation_id="UpdateDessert"
)
async def update_dessert(dessert_id: int, dessert: DessertIn):
    with rt.session() as session:
        model = session.get(Dessert, dessert_id)
        if not model:
            raise HTTPException(status_code=404, detail="Dessert not found")
        model.update_from_in(dessert)
        session.commit()
        session.refresh(model)
        return DessertOut.from_model(model)


@app.delete("/desserts/{dessert_id}", response_model=None, operation_id="DeleteDessert")
async def delete_dessert(dessert_id: int):
    with rt.session() as session:
        model = session.get(Dessert, dessert_id)
        if not model:
            raise HTTPException(status_code=404, detail="Dessert not found")
        session.delete(model)
        session.commit()


@app.get(
    "/desserts/events",
    operation_id="DessertsEvents",
    response_model=list[NotificationOut],
)
async def desserts_events(request: Request):
    """Server-Sent Events endpoint for real-time dessert updates."""
    rt.logger.info("Starting pg_event_stream")

    async def pg_event_stream() -> AsyncGenerator[str, None]:
        rt.logger.info("Connecting to database")
        info = rt.get_connection_info()
        conn = None

        try:
            conn = await asyncpg.connect(
                host=info.host,
                port=info.port,
                user=info.user,
                password=info.password,
                database=info.database,
            )
            rt.logger.info("Connected to database")

            queue: asyncio.Queue[Notification] = asyncio.Queue()
            rt.logger.info(f"Adding listener to database on channel {NOTIFY_CHANNEL}")

            def notify_callback(_, __, ___, raw_notification: str):
                notification = Notification.model_validate_json(raw_notification)
                queue.put_nowait(notification)

            await conn.add_listener(NOTIFY_CHANNEL, notify_callback)
            rt.logger.info("Listener added to database")

            while True:
                # Check if client has disconnected
                if await request.is_disconnected():
                    rt.logger.info("Client disconnected, closing SSE stream")
                    break

                try:
                    notification = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield f"data: {notification.to_out().model_dump_json()}\n\n"
                except asyncio.TimeoutError:
                    # Send heartbeat and check connection
                    yield ": heartbeat\n\n"
                except asyncio.CancelledError:
                    rt.logger.info("SSE stream cancelled")
                    break
                except Exception as e:
                    rt.logger.error(f"Error in pg_event_stream: {e}")
                    yield f"data: error: {e}\n\n"
                    break

        except asyncio.CancelledError:
            rt.logger.info("SSE stream cancelled during setup")
        except Exception as e:
            rt.logger.error(f"Error in pg_event_stream: {e}")
            yield f"data: error: {e}\n\n"

        finally:
            if conn:
                await conn.close()
                rt.logger.info("Database connection closed")

    return StreamingResponse(
        pg_event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
        },
    )


app.openapi = partial(custom_openapi, app)
