import logging
import threading
from contextlib import asynccontextmanager

import uvicorn
from application_sdk.app.rest import FastAPIApplicationBuilder
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.workflow import PostgresWorkflowBuilder

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    atlan_app_builder.on_api_service_start()
    if (
        atlan_app_builder.workflow_builder_interface
        and atlan_app_builder.workflow_builder_interface.worker_interface
    ):
        worker_thread = threading.Thread(
            target=atlan_app_builder.start_worker, daemon=True
        )
        worker_thread.start()
    yield


app = FastAPI(title="Postgres App", lifespan=lifespan)


if __name__ == "__main__":
    postgres_workflow = PostgresWorkflowBuilder()

    atlan_app_builder = FastAPIApplicationBuilder(app, postgres_workflow)
    atlan_app_builder.add_telemetry_routes()
    atlan_app_builder.add_workflows_router()

    # always mount the frontend at the end
    app.mount(
        "/", StaticFiles(directory="frontend/.output/public", html=True), name="static"
    )

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )

    # atlan_app_builder.configure_open_telemetry()
