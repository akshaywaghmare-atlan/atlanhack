import asyncio
import logging
import os
import threading
from contextlib import asynccontextmanager

from application_sdk.app.rest.fastapi import (
    FastAPIApplication,
    FastAPIApplicationConfig,
    HttpWorkflowTrigger,
)
from application_sdk.workflows.resources.temporal_resource import (
    TemporalConfig,
    TemporalResource,
)
from application_sdk.workflows.sql.controllers.auth import SQLWorkflowAuthController
from application_sdk.workflows.sql.resources.sql_resource import SQLResourceConfig
from application_sdk.workflows.sql.workflows.workflow import SQLWorkflow
from application_sdk.workflows.workers.worker import WorkflowWorker
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.workflow import (
    PostgreSQLResource,
    PostgresWorkflowBuilder,
    PostgresWorkflowMetadata,
    PostgresWorkflowPreflight,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await fastapi_app.on_app_start()

    worker: WorkflowWorker = WorkflowWorker(
        temporal_resource=temporal_resource,
        temporal_activities=postgres_workflow.get_activities(),
        workflow_classes=[SQLWorkflow],
    )

    worker_thread = threading.Thread(
        target=lambda: asyncio.run(worker.start()), daemon=True
    )
    worker_thread.start()
    yield


APPLICATION_NAME = "postgres"
APP_HOST = os.getenv("ATLAN_APP_HTTP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("ATLAN_APP_HTTP_PORT", 8000))
APP_DASHBOARD_HOST = os.getenv("ATLAN_APP_DASHBOARD_HTTP_HOST", "0.0.0.0")
APP_DASHBOARD_PORT = int(os.getenv("ATLAN_APP_DASHBOARD_HTTP_PORT", 8050))

if __name__ == "__main__":
    # Creating resources
    sql_resource = PostgreSQLResource(SQLResourceConfig())
    temporal_resource = TemporalResource(
        TemporalConfig(
            application_name=APPLICATION_NAME,
        )
    )
    asyncio.run(temporal_resource.load())

    # Creating controllers
    metadata_controller = PostgresWorkflowMetadata(sql_resource=sql_resource)
    preflight_check_controller = PostgresWorkflowPreflight(sql_resource=sql_resource)
    auth_controller = SQLWorkflowAuthController(sql_resource=sql_resource)

    # Creating workflow
    postgres_workflow: SQLWorkflow = (  # type: ignore
        PostgresWorkflowBuilder()
        .set_sql_resource(sql_resource=sql_resource)
        .set_temporal_resource(temporal_resource=temporal_resource)
        .set_preflight_check_controller(
            preflight_check_controller=preflight_check_controller
        )
        .build()
    )

    # Creating FastAPI application
    fastapi_app = FastAPIApplication(
        auth_controller=auth_controller,
        metadata_controller=metadata_controller,
        preflight_check_controller=preflight_check_controller,
        config=FastAPIApplicationConfig(
            host=os.getenv("APP_HOST", "0.0.0.0"),
            port=int(os.getenv("APP_PORT", 8000)),
            lifespan=lifespan,
        ),
    )
    fastapi_app.register_workflow(
        postgres_workflow,
        triggers=[
            HttpWorkflowTrigger(
                endpoint="/start",
                methods=["POST"],
            )
        ],
    )

    # Set up templates and static files
    templates = Jinja2Templates(directory="frontend/templates")

    @fastapi_app.app.get("/")
    async def home(request: Request):
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "app_dashboard_http_port": APP_DASHBOARD_PORT,
                "app_dashboard_http_host": APP_DASHBOARD_HOST,
                "app_http_port": APP_PORT,
                "app_http_host": APP_HOST,
            },
        )

    # Mount static files first
    fastapi_app.app.mount("/", StaticFiles(directory="frontend/static"), name="static")

    # Starting FastAPI application
    asyncio.run(fastapi_app.start())

    # atlan_app_builder.configure_open_telemetry()
