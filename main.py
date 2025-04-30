import asyncio

from application_sdk.application.metadata_extraction.sql import (
    BaseSQLMetadataExtractionApplication,
)
from application_sdk.constants import APPLICATION_NAME

from app.clients import SQLClient
from app.transformers.atlas import SQLAtlasTransformer


async def main():
    # Initialize the application
    application = BaseSQLMetadataExtractionApplication(
        name=APPLICATION_NAME,
        client_class=SQLClient,
        transformer_class=SQLAtlasTransformer,
    )

    # Setup the workflow
    await application.setup_workflow()

    # Start the worker
    await application.start_worker()

    # Setup the application server
    await application.setup_server()

    # Start the application server
    await application.start_server()


if __name__ == "__main__":
    asyncio.run(main())
