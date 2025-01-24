import asyncio
import logging
import os

from application_sdk.application.fastapi import FastAPIApplication, HttpWorkflowTrigger
from application_sdk.clients.temporal import TemporalClient
from application_sdk.common.logger_adaptors import AtlanLoggerAdapter
from application_sdk.worker import Worker
from application_sdk.workflows.metadata_extraction.sql import (
    SQLMetadataExtractionWorkflow,
)
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.workflow import (
    CustomTransformer,
    PostgresActivities,
    PostgreSQLClient,
    PostgresWorkflowHandler,
)

logger = AtlanLoggerAdapter(logging.getLogger(__name__))

APPLICATION_NAME = os.getenv("ATLAN_APPLICATION_NAME", "postgres")
APP_HOST = os.getenv("ATLAN_APP_HTTP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("ATLAN_APP_HTTP_PORT", 8000))
APP_DASHBOARD_HOST = os.getenv("ATLAN_APP_DASHBOARD_HTTP_HOST", "0.0.0.0")
APP_DASHBOARD_PORT = int(os.getenv("ATLAN_APP_DASHBOARD_HTTP_PORT", 8050))
TENANT_ID = os.getenv("ATLAN_TENANT_ID", "default")
ATLAN_APPLICATION_NAME = os.getenv("ATLAN_APPLICATION_NAME", "postgres")

# Set up templates
templates = Jinja2Templates(directory="frontend/templates")


async def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "app_dashboard_http_port": APP_DASHBOARD_PORT,
            "app_dashboard_http_host": APP_DASHBOARD_HOST,
            "app_http_port": APP_PORT,
            "app_http_host": APP_HOST,
            "tenant_id": TENANT_ID,
            "app_name": ATLAN_APPLICATION_NAME,
        },
    )


def setup_routes(app: FastAPIApplication):
    app.app.get("/")(home)
    # Mount static files
    app.app.mount("/", StaticFiles(directory="frontend/static"), name="static")


async def initialize_and_start():
    # Creating resources
    sql_client = PostgreSQLClient()
    temporal_client = TemporalClient(application_name=APPLICATION_NAME)
    await temporal_client.load()

    # Creating controllers
    handler = PostgresWorkflowHandler(sql_client=sql_client)

    activities = PostgresActivities(
        sql_client_class=PostgreSQLClient,
        handler_class=PostgresWorkflowHandler,
        transformer_class=CustomTransformer,
    )

    # Creating workflow
    worker: Worker = Worker(
        temporal_client=temporal_client,
        workflow_classes=[SQLMetadataExtractionWorkflow],
        temporal_activities=SQLMetadataExtractionWorkflow.get_activities(activities),
    )

    # Creating FastAPI application
    fast_api_app = FastAPIApplication(
        handler=handler,
        temporal_client=temporal_client,
    )
    fast_api_app.register_workflow(
        SQLMetadataExtractionWorkflow,
        [
            HttpWorkflowTrigger(
                endpoint="/start",
                methods=["POST"],
                workflow_class=SQLMetadataExtractionWorkflow,
            )
        ],
    )
    # Setup routes
    setup_routes(fast_api_app)

    # Start worker in background
    await worker.start(daemon=True)
    # Starting FastAPI application
    await fast_api_app.start()


if __name__ == "__main__":
    asyncio.run(initialize_and_start())
    # atlan_app_builder.configure_open_telemetry()
