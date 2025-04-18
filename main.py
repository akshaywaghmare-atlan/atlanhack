import asyncio

from application_sdk.activities.metadata_extraction.sql import (
    BaseSQLMetadataExtractionActivities,
)
from application_sdk.application.fastapi import Application, HttpWorkflowTrigger
from application_sdk.clients.utils import get_workflow_client
from application_sdk.handlers.sql import SQLHandler
from application_sdk.worker import Worker
from application_sdk.workflows.metadata_extraction.sql import (
    BaseSQLMetadataExtractionWorkflow,
)

from app.clients import SQLClient
from app.transformers.atlas import SQLAtlasTransformer


async def main():
    # setup workflow client for worker and application server
    workflow_client = get_workflow_client()
    await workflow_client.load()

    # setup sql metadata extraction activities
    # requires a sql client for source connectivity, handler for preflight checks, transformer for atlas mapping
    activities = BaseSQLMetadataExtractionActivities(
        sql_client_class=SQLClient,
        handler_class=SQLHandler,
        transformer_class=SQLAtlasTransformer,
    )

    # setup and start worker for workflow and activities execution
    worker: Worker = Worker(
        workflow_client=workflow_client,
        workflow_classes=[BaseSQLMetadataExtractionWorkflow],
        workflow_activities=BaseSQLMetadataExtractionWorkflow.get_activities(
            activities
        ),
    )
    await worker.start()

    # setup application server. serves the UI, and handles the various triggers
    app = Application(
        handler=SQLHandler(sql_client=SQLClient()),
        workflow_client=workflow_client,
    )

    # register the workflow on the application server
    # the workflow is by default triggered by an HTTP POST request to the /start endpoint
    app.register_workflow(
        workflow_class=BaseSQLMetadataExtractionWorkflow,
        triggers=[HttpWorkflowTrigger()],
    )
    await app.start()


if __name__ == "__main__":
    asyncio.run(main())
