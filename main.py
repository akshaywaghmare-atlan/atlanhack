import asyncio
import logging
import threading
from contextlib import asynccontextmanager

from application_sdk.app.rest.fastapi import (
    FastAPIApplication,
    FastApiApplicationConfig,
)
from application_sdk.workflows.resources.temporal_resource import (
    TemporalConfig,
    TemporalResource,
)
from application_sdk.workflows.sql.controllers.auth import SQLWorkflowAuthController
from application_sdk.workflows.sql.resources.sql_resource import SQLResourceConfig
from application_sdk.workflows.sql.workflows.workflow import SQLWorkflow
from application_sdk.workflows.workers.worker import WorkflowWorker
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

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

if __name__ == "__main__":
    # Creating resources
    sql_resource = PostgreSQLResource(SQLResourceConfig())
    temporal_resource = TemporalResource(
        TemporalConfig(
            application_name=APPLICATION_NAME,
        )
    )
    asyncio.run(temporal_resource.load())

    # Creating workflow
    postgres_workflow: SQLWorkflow = (
        PostgresWorkflowBuilder()
        .set_sql_resource(sql_resource=sql_resource)
        .set_temporal_resource(temporal_resource=temporal_resource)
        .build()
    )

    # Creating FastAPI application
    fastapi_app = FastAPIApplication(
        auth_controller=SQLWorkflowAuthController(sql_resource=sql_resource),
        metadata_controller=PostgresWorkflowMetadata(sql_resource=sql_resource),
        preflight_check_controller=PostgresWorkflowPreflight(sql_resource=sql_resource),
        workflow=postgres_workflow,
        config=FastApiApplicationConfig(
            host="0.0.0.0",
            port=8000,
            lifespan=lifespan,
        ),
    )
    fastapi_app.app.mount(
        "/", StaticFiles(directory="frontend", html=True), name="static"
    )

    # Starting FastAPI application
    asyncio.run(fastapi_app.start())

    # atlan_app_builder.configure_open_telemetry()
