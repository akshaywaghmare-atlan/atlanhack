import asyncio
import time

from application_sdk.application.metadata_extraction.sql import (
    BaseSQLMetadataExtractionApplication,
)
from application_sdk.common.error_codes import ApiError
from application_sdk.constants import APPLICATION_NAME
from application_sdk.observability.logger_adaptor import get_logger
from application_sdk.observability.metrics_adaptor import MetricType, get_metrics
from application_sdk.transformers.query import QueryBasedTransformer

from app.clients import SQLClient


async def main():
    # Initialize logger and metrics
    logger = get_logger(__name__)
    metrics = get_metrics()

    try:
        logger.info("Starting application initialization")
        start_time = time.time()

        # Initialize the application
        application = BaseSQLMetadataExtractionApplication(
            name=APPLICATION_NAME,
            client_class=SQLClient,
            transformer_class=QueryBasedTransformer,  # type: ignore
        )

        # Setup the workflow
        logger.info("Setting up workflow")
        await application.setup_workflow()
        metrics.record_metric(
            name="workflow_setup_success",
            value=1,
            metric_type=MetricType.COUNTER,
            labels={"application": APPLICATION_NAME},
            description="Successful workflow setup",
            unit="count",
        )

        # Start the worker
        logger.info("Starting worker")
        await application.start_worker()
        metrics.record_metric(
            name="worker_start_success",
            value=1,
            metric_type=MetricType.COUNTER,
            labels={"application": APPLICATION_NAME},
            description="Successful worker start",
            unit="count",
        )

        # Setup the application server
        logger.info("Setting up application server")
        await application.setup_server()
        metrics.record_metric(
            name="server_setup_success",
            value=1,
            metric_type=MetricType.COUNTER,
            labels={"application": APPLICATION_NAME},
            description="Successful server setup",
            unit="count",
        )

        # Start the application server
        logger.info("Starting application server")
        await application.start_server()

        # Record application startup duration
        duration = (time.time() - start_time) * 1000  # Convert to milliseconds
        metrics.record_metric(
            name="application_startup_duration",
            value=duration,
            metric_type=MetricType.HISTOGRAM,
            labels={"application": APPLICATION_NAME},
            description="Application startup duration",
            unit="milliseconds",
        )

        logger.info(f"Application started successfully in {duration:.2f}ms")

    except Exception as e:
        # Record application startup failure
        metrics.record_metric(
            name="application_startup_failure",
            value=1,
            metric_type=MetricType.COUNTER,
            labels={"application": APPLICATION_NAME, "error": str(e)},
            description="Application startup failures",
            unit="count",
        )

        logger.error(
            f"Failed to start application: {str(e)}",
            extra={"error_code": ApiError.SERVER_START_ERROR.code},
        )
        raise


if __name__ == "__main__":
    asyncio.run(main())
