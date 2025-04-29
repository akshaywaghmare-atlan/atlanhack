import asyncio

from application_sdk.application.metadata_extraction.sql import (
    BaseSQLMetadataExtractionApplication,
)
from application_sdk.constants import APPLICATION_NAME

from app.clients import SQLClient
from app.transformers.atlas import SQLAtlasTransformer


async def main():
    application = BaseSQLMetadataExtractionApplication(
        name=APPLICATION_NAME,
        sql_client_class=SQLClient,
        transformer_class=SQLAtlasTransformer,
    )

    await application.setup_workflow()
    await application.setup_server()
    await application.start_server()


if __name__ == "__main__":
    asyncio.run(main())
